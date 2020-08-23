import math

'''
This problem can be solved in 2D space (x, z) because when y = 0 the angle the mirror is at needs to be the steepest
note: this assumes mirror thickness == 0, you can adjust degrees of overcoverage to account for mirror thickness
'''

edge_a = 10 # distance from camera to where z = 0
edge_b = 4 # distance from far side of the slot where the mouse reaches out from to the inner edge of the mirror
degrees_of_overcoverage = 5 # how many degrees past z=0 do you want?

# this func returns the angle of the mirror relative to the z-axis
def get_angle(edge_a, edge_b, degrees_of_overcoverage):
    edge_x = edge_b * math.tan(math.radians(degrees_of_overcoverage))
    edge_e = (edge_a + edge_x)/2 - edge_x
    theta_C = math.degrees(math.atan(edge_e/edge_b))
    theta_F = 90 - theta_C
    theta_D = 90 - theta_F
    return theta_D
print(get_angle(edge_a, edge_b, degrees_of_overcoverage))