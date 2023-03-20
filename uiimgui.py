from collections import deque
import numpy as np

from imgui_bundle import imgui, immapp, implot, ImVec2, hello_imgui
#from imgui_bundle import imgui_md
from imgui_bundle.demos_python import demo_utils

import kernel

# Struct that holds the application's state
class AppState:
    f: float = 0.0
    counter: int = 0
    rocket_progress: float = 0.0
    button_ros: str = "?"
    button_neuro: str = "?"
    button_kinem: str = "?"
    button_decode: str = "?"
    label_mode: str = "?"
    label_log: str = "?"
    buffer0: deque = deque([], maxlen = 100)
    buffer1: deque = deque([], maxlen = 100)

# CommandGui: the widgets on the left panel
def command_gui(state: AppState):

    _update(state)

    if imgui.button(state.button_neuro):
        if state.button_neuro == "StartNeuro":
            kernel.exec("start","Neuro")
        else:
            kernel.exec("stop","Neuro")
    
    if imgui.button(state.button_kinem):
        if state.button_kinem == "StartKinem":
            kernel.exec("start","Kinem")
        else:
            kernel.exec("stop","Kinem")
    
    if imgui.button(state.button_decode):
        neural = kernel.state.modules["Neuro"]
        if state.button_decode == "Train":
            neural.message = "SwitchToTrain"
        else:
            neural.message = "SwitchToDecode"
    
    imgui.text(state.label_mode)
    imgui.text(state.label_log)

    #import time
    #time.sleep(0.01)

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

def _update(state: AppState):

    # Update buttons
    if kernel.state.modules["Neuro"].state == "Running":
        state.button_neuro = "StopNeuro"
    else:
        state.button_neuro = "StartNeuro"
    
    if kernel.state.modules["Kinem"].state == "Running":
        state.button_kinem = "StopKinem"
    else:
        state.button_kinem = "StartKinem"
    
    if kernel.state.modules["Neuro"].mode == "Decoding":
        state.button_decode = "Train"
    else:
        state.button_decode = "Decode"

    # Update labels
    state.label_mode = kernel.state.modules["Neuro"].mode
    state.label_log = kernel.state.modules["Neuro"].log

    # Update trace    
    state.buffer0.append(kernel.state.x_current)    
    state.buffer1.append(kernel.state.x_pred)

def plot_gui(state: AppState):
    implot.push_colormap(implot.Colormap_.deep)
    plot_height = immapp.em_size() * 20    
    if implot.begin_plot("Plot", ImVec2(-1, plot_height)):
        implot.setup_axes("x-axis", "y-axis")
        implot.setup_axes_limits(-0.2, 1.2, -0.2, 1.2)        
        x = np.hstack(state.buffer0)
        x_pred = np.hstack(state.buffer1)
        implot.plot_line("x", x[0,:], x[1,:])
        implot.plot_line("x_pred", x_pred[0,:], x_pred[1,:])
        implot.end_plot()
        #if len(state.buffer0) > 50:
        #    from IPython import embed; embed()

def show_menu_gui():
    if imgui.begin_menu("Menu"):
        clicked, _ = imgui.menu_item("Test", "", False)
        if clicked:
            hello_imgui.log(hello_imgui.LogLevel.warning, "It works")
        imgui.end_menu()

def show_app_menu_items():
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
    run_params.app_window_params.window_geometry.size = (600, 500)
    run_params.app_window_params.restore_previous_geometry = True

    # Default HelloImGui status bar
    run_params.imgui_window_params.show_status_bar = False
    
    # Default HelloImGui menu bar
    run_params.imgui_window_params.show_menu_bar = True
    run_params.callbacks.show_menus = show_menu_gui
    run_params.callbacks.show_app_menu_items = show_app_menu_items

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
    commands_panel.gui_function = lambda: command_gui(state)
    # Main panel
    main_panel = hello_imgui.DockableWindow()
    main_panel.label = "Plot"
    main_panel.dock_space_name = "MainDockSpace"
    main_panel.gui_function = lambda: plot_gui(state)
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
    ]

    # Run the app
    addons_params = immapp.AddOnsParams()
    addons_params.with_markdown = True
    addons_params.with_implot = True    
    immapp.run(run_params, addons_params)    

if __name__ == "__main__":
    start()
