import time,threading
from collections import deque
import numpy as np

from imgui_bundle import imgui, immapp, implot, ImVec2, hello_imgui
from imgui_bundle.demos_python import demo_utils

import utils.comm as comm
import utils.shared as shared

# NOTE: this could be used to initialize the variables each node requires
import rt2.vars as vars

shared.x_current = np.array([[0.0,0.0,0.0]],dtype=np.float32).T
shared.x_pred = np.array([[0.0,0.0,0.0]],dtype=np.float32).T
shared.x_pred_local = np.array([[0.0,0.0,0.0]],dtype=np.float32).T
shared.p_neuro = np.array([0.0],dtype=np.float32)
shared.p_kinem = np.array([0.0],dtype=np.float32)

# Struct that holds the application's state
class AppState:
    f: float = 0.0
    counter: int = 0
    rocket_progress: float = 0.0
    button_ros: str = "?"
    button_neuro: str = "?StartNeuro"
    button_kinem: str = "?StartKinem"
    button_kinem_dec: str = "?StartKinemDec (Disabled)"
    separator_modes: str = "Modes"
    button_idle: str = "Idle (& Train for now)"
    button_collect: str = "Collect"
    button_collect_and_decode: str = "Collect/Decode"
    label_mode: str = "?"
    label_log: str = "?"
    buffer0: deque = deque([], maxlen = 100)
    buffer1: deque = deque([], maxlen = 100)
    buffer2: deque = deque([], maxlen = 100)
    buffer3: list = []
    buffer4: list = []
    plot3: np.array = np.array([])
    plot4: np.array = np.array([])

def _handle_updates(state: AppState):

    # Update buttons    
    if 'neuro' in nodes:
        if nodes['neuro']['up'] == 0:
            state.button_neuro = "StartNeuro"
        else:
            state.button_neuro = "StopNeuro"

        if nodes["neuro"]["mode"] == vars.IDLE:
            state.label_mode = "Idling"
        elif nodes["neuro"]["mode"] == vars.COLLECT:
            state.label_mode = "Collecting"
        elif nodes["neuro"]["mode"] == vars.COLLECT_AND_DECODE:
            state.label_mode = "Collecting and decoding"
        
        state.label_log = nodes["neuro"]["log"]

    if 'kinem' in nodes:
        if nodes['kinem']['up'] == 0:
            state.button_kinem = "StartKinem"
        else:
            state.button_kinem = "StopKinem"

    if 'kinemdec' in nodes:
        if nodes['kinemdec']['up'] == 0:
            state.button_kinem_dec = "StartKinemDec"
        else:
            state.button_kinem_dec = "StopKinemDec"

    # Update traces
    # We make copies because otherwise we will have just an array of 
    # pointers to the same shared memory block
    state.buffer0.append(np.copy(shared.x_current))
    state.buffer1.append(np.copy(shared.x_pred_local))
    state.buffer2.append(np.copy(shared.x_pred))
    state.buffer3.append(np.copy(shared.p_neuro))
    state.buffer4.append(np.copy(shared.p_kinem))

    if len(state.buffer3) == 100:
        state.plot3 = np.array(state.buffer3)        
        state.buffer3.clear()
        state.plot4 = np.array(state.buffer4)
        state.buffer4.clear()

# CommandGui: the widgets on the left panel
def _display_commands(state: AppState):

    _handle_updates(state)

    if imgui.button(state.button_neuro):
        if state.button_neuro == "StartNeuro":
            uinode.send("start", nodes['neuro']['ip'], nodes['neuro']['port'])
        else:
            uinode.send("stop", nodes['neuro']['ip'], nodes['neuro']['port'])
    
    if imgui.button(state.button_kinem):
        if state.button_kinem == "StartKinem":
            uinode.send("start", nodes['kinem']['ip'], nodes['kinem']['port'])
        else:
            uinode.send("stop", nodes['kinem']['ip'], nodes['kinem']['port'])

    if imgui.button(state.button_kinem_dec):
        if state.button_kinem_dec == "StartKinemDec":
            uinode.send("start", nodes['kinemdec']['ip'], nodes['kinemdec']['port'])
        else:
            uinode.send("stop", nodes['kinemdec']['ip'], nodes['kinemdec']['port'])

    imgui.separator_text(state.separator_modes)

    if imgui.button(state.button_idle):
        uinode.send("switch_to idle", nodes['neuro']['ip'], nodes['neuro']['port'])
    elif imgui.button(state.button_collect):
        uinode.send("switch_to collect", nodes['neuro']['ip'], nodes['neuro']['port'])
    elif imgui.button(state.button_collect_and_decode):
        uinode.send("switch_to collect_and_decode", nodes['neuro']['ip'], nodes['neuro']['port'])
    
    #    if state.button_decode == "Train":
    #        uinode.send("switch_to Train", nodes['neuro']['ip'], nodes['neuro']['port'])
    #    else:            
    #        uinode.send("switch_to Decode", nodes['neuro']['ip'], nodes['neuro']['port'])

    imgui.text(state.label_mode)
    imgui.text(state.label_log)

    # Without this, the ROS subscriber thread is starved for
    # some weird reason
    time.sleep(0.001)

    #imgui.same_line()
    # imgui_md.render_unindented(
    #     """
    #     # Basic widgets demo
    #     """
    # )
    # # Edit 1 float using a slider from 0.0f to 1.0f
    # changed, state.f = imgui.slider_float("float", state.f, 0.0, 1.0)
    # if changed:
    #     hello_imgui.log(hello_imgui.LogLevel.warning, f"state.f was changed to {state.f}")

def _display_plots(state: AppState):
    implot.push_colormap(implot.Colormap_.deep)    
    ems = immapp.em_size()
    imgui.same_line()    
    if implot.begin_plot("Plot0", ImVec2(35*ems, 30*ems)):
        implot.setup_axes("x-axis", "y-axis")
        implot.setup_axes_limits(-0.2, 1.2, -0.2, 1.2)        
        x0 = np.hstack(state.buffer0)        
        x1 = np.hstack(state.buffer1)
        x2 = np.hstack(state.buffer2)
        implot.plot_line("x", x0[0,:], x0[1,:])
        implot.set_next_marker_style(2,1.2)
        implot.plot_line("x_p_mon", x1[0,:], x1[1,:])
        implot.plot_line("x_p_dec", x2[0,:], x2[1,:])
        implot.end_plot()
        #if len(state.buffer0) > 50:
        #    from IPython import embed; embed()
    imgui.same_line()
    imgui.begin_group()
    if implot.begin_plot("Plot1", ImVec2(30*ems, 25*ems)):
        implot.setup_axes("x-axis", "y-axis")
        implot.setup_axes_limits(0.0, 100.0, 0, 0.2)        
        implot.plot_line("x0_neu", state.plot3)
        implot.plot_line("x1_kin", state.plot4)
        implot.end_plot()
    if implot.begin_plot("Plot2", ImVec2(30*ems, 25*ems)):
        implot.setup_axes("x-axis", "y-axis")
        implot.setup_axes_limits(-0.2, 1.2, -0.2, 1.2)
        implot.end_plot()
    imgui.end_group()


lines = []
def _display_tests(state: AppState):
    imgui.text("Hello")
    #imgui.begin("Circle")
    imgui.text("Hello2")
    cursor = imgui.get_cursor_screen_pos()
    draw_list = imgui.get_window_draw_list()

    io = imgui.get_io()
    cursor_pos = ImVec2(io.mouse_pos.x,io.mouse_pos.y)

    lines.append(cursor_pos)
    if len(lines)>100:
        lines.pop(0)

    imgui.invisible_button("Canvas",ImVec2(100.0,100.0),imgui.ButtonFlags_.mouse_button_right)
    imgui.is_item_hovered

    draw_list.add_circle(cursor_pos,10.0,imgui.IM_COL32(255, 155, 255, 255), thickness=1.0)
    draw_list.add_polyline(lines,imgui.IM_COL32(255, 255, 255, 255),0,1)

    imgui.button("Hello")
    #imgui.end()

def _handle_menu():
    if imgui.begin_menu("Menu"):
        clicked, _ = imgui.menu_item("Test", "", False)
        if clicked:
            hello_imgui.log(hello_imgui.LogLevel.warning, "It works")
        imgui.end_menu()

def _handle_menu_items():
    clicked, _ = imgui.menu_item("Item", "", False)
    if clicked:
        hello_imgui.log(hello_imgui.LogLevel.info, "Clicked item")

def start():

    # HelloImGui assets dir (fonts, images, etc.)
    hello_imgui.set_assets_folder(demo_utils.demos_assets_folder())

    # HelloImGui default params (settings and callbacks)
    run_params = hello_imgui.RunnerParams()

    # Do not idle
    run_params.fps_idling = hello_imgui.FpsIdling()
    run_params.fps_idling.enable_idling = False

    # Window title sets the name of the ini files
    # Docking_demo.ini (imgui settings) and Docking_demo_appWindow.ini (window geom.)
    run_params.app_window_params.window_title = "monitor"
    run_params.imgui_window_params.menu_app_title = "MonitorApp"
    run_params.app_window_params.window_geometry.size = (800, 500)
    run_params.app_window_params.restore_previous_geometry = True

    # Default HelloImGui status bar
    run_params.imgui_window_params.show_status_bar = False
    
    # Default HelloImGui menu bar
    run_params.imgui_window_params.show_menu_bar = True
    run_params.callbacks.show_menus = _handle_menu
    run_params.callbacks.show_app_menu_items = _handle_menu_items

    # Setup docking
    # Create horizontal split
    split_main_bottom = hello_imgui.DockingSplit()
    split_main_bottom.initial_dock = "MainDockSpace"
    split_main_bottom.new_dock = "BottomSpace"
    split_main_bottom.direction = imgui.Dir_.down
    split_main_bottom.ratio = 0.25
    # Create vertical split
    split_main_left = hello_imgui.DockingSplit()
    split_main_left.initial_dock = "MainDockSpace"
    split_main_left.new_dock = "LeftSpace"
    split_main_left.direction = imgui.Dir_.left
    split_main_left.ratio = 0.25    
    # Tell HelloImGui that we want a full screen dock space
    run_params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
    )
    # Enable drag panels outside out the main window
    run_params.imgui_window_params.enable_viewports = True
    # Do not persist layout
    run_params.docking_params.layout_condition = hello_imgui.DockingLayoutCondition.application_start    
    # Set splits on HelloImGui
    run_params.docking_params.docking_splits = [split_main_bottom, split_main_left]

    # Define the application state
    state = AppState()

    # Define dockable panels
    # Command panel
    commands_panel = hello_imgui.DockableWindow()
    commands_panel.label = "Commands"
    commands_panel.dock_space_name = "LeftSpace"
    commands_panel.gui_function = lambda: _display_commands(state)
    # Main panel
    main_panel = hello_imgui.DockableWindow()
    main_panel.label = "Plot"
    main_panel.dock_space_name = "MainDockSpace"
    main_panel.gui_function = lambda: _display_plots(state)
    # Test panel
    tests_panel = hello_imgui.DockableWindow()
    tests_panel.label = "Tests"
    tests_panel.dock_space_name = "MainDockSpace"
    tests_panel.gui_function = lambda: _display_tests(state)
    # Log panel
    logs_panel = hello_imgui.DockableWindow()
    logs_panel.label = "Logs"
    logs_panel.dock_space_name = "BottomSpace"
    logs_panel.gui_function = hello_imgui.log_gui

    # Finally, transmit these windows to HelloImGui
    run_params.docking_params.dockable_windows = [
        commands_panel,
        logs_panel,
        main_panel,
        tests_panel,
    ]

    # Run the app
    addons_params = immapp.AddOnsParams()
    addons_params.with_markdown = True
    addons_params.with_implot = True    
    immapp.run(run_params, addons_params)    

class UINode(comm.Node):
    def start(self):
        print("uiimgui.py: running UINode loop", threading.get_ident())
        super().start()

    def stop(self):
        print("uiimgui.py: stopping UINode loop")
        super().stop()

    def send(self, msg, tgt,port):
        self.sock.sendto(msg.encode(), (tgt,port))
        print("uiimgui.py: UINode sent", msg, tgt, port)

    def listener_callback(self, msg):        
        msg = msg.data.decode().split()
        if msg[0] not in nodes:
            nodes[msg[0]] = {}
        for s in msg[1:]:
            k,v = s.split('=')
            if v.isdigit():
                nodes[msg[0]][k] = int(v)
            else:
                nodes[msg[0]][k] = v
        print("uiimgui.py: UINode state:")
        print("\n".join("{}\t{}".format(k, v) for k, v in nodes.items()))

nodes = {}
uinode = UINode(16000)

if __name__ == "__main__":    
    threading.Thread(target=start, daemon=True).start()
    uinode.start()