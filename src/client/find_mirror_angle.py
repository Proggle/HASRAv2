import math

'''
problem can be solved in 2D space (x, z) because when y = 0 the angle the mirror is at needs to be the steepest
'''

edge_a = 4 # distance from camera to where z = 0
edge_b = 4 # distance from far side of the slot where the mouse reaches out from to the inner edge of the mirror
degrees_of_overcoverage = 5 # how many degrees past z=0 do you want?

edge_x = edge_b * math.tan(math.radians(degrees_of_overcoverage))
edge_e = (edge_a + edge_x)/2 - edge_x

theta_C = math.degrees(math.atan(edge_e/edge_b))

theta_F = 90 - theta_C

theta_D = 90 - theta_F

print(theta_D)