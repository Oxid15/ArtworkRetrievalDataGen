# The folder with images to render on the wall
source_folder = "src"

# The folder to place renders
destination_folder = "dst"

# The angles and distance are the spherical coordinates of the camera
# given that the position of the object in the scene is (0,0,0)
# render_per_input times different angles and distances are sampled
# from these ranges
camera_angles_range = [[70, -60], [110, 60]]

camera_distance_range = [3, 5]

render_per_input = 1
