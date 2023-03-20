# import rclpy
# from rclpy.node import Node
# from std_msgs.msg import Float32MultiArray
# from rcl_interfaces.srv import SetParameters
# from rclpy import Parameter

# class Ros2Comm(Node):
#     def __init__(self):
#         super().__init__('gui_subscriber')
#         self.subscription = self.create_subscription(Float32MultiArray,
#             'topic0', self.listener_callback, 10)
#         self.subscription  # prevent unused variable warning
#         #self.client = self.create_client(Trigger,'stateservice')
#         self.client = self.create_client(SetParameters,'stateservice')
#         self.t0 = time.time()
#
#     def listener_callback(self, msg):        
#         #time_elapsed = time.time() - self.t0
#         #off0 = offset0.value
#         #off1 = offset1.value
#         #buffer.send(np.array([[msg.data[0],msg.data[1]+off0+off1]]))
#         self.get_logger().info('Topic: %f %f' % (msg.data[0], msg.data[1]))

# def ros_loop():
#     global minimal_subscriber
#     print("ROS thread started")    
#     rclpy.init()
#     minimal_subscriber = Ros2Comm()    
#     # This is apparently an OK way to work with GUIs
#     # https://answers.ros.org/question/320474/ros2-correct-usage-of-spin_once-to-receive-multiple-callbacks-synchronized/
#     # https://answers.ros.org/question/296480/functional-difference-between-ros2-spin_some-spin_once-and-spin_until_future/
#     # TODO this wont die if no messages are received
#     while rclpy.ok() and not kill_ros:
#         rclpy.spin_once(minimal_subscriber, timeout_sec=1)
#     if rclpy.ok():
#         # Destroy the node explicitly
#         # (optional - otherwise it will be done automatically
#         # when the garbage collector destroys the node object)
#         minimal_subscriber.destroy_node()
#         rclpy.shutdown()
#         print("ROS thread ended")
