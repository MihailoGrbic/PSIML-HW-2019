import numpy as np
from PIL import Image
import math
import random

class body:
    def __init__(self, index = None, x_cord = None, y_cord = None, shape = None):
        self.index = index
        self.x_cord = x_cord
        self.y_cord = y_cord
        self.shape = shape

def find_bodies(img):
    bodies = []
    binarized = img > 0
    
    for i in range(0, img.shape[0]):                                                  #using BFS instead of DFS, because DFS breaks Python's recursion stack limit
        for j in range(0, img.shape[1]):
            if binarized[i, j]:                                                                                                         
                binarized[i, j] = False                           
                to_check = [(i, j)]
                elements = []
                x_sum = 0
                y_sum = 0
                count = 0

                while len(to_check) > 0:                                                                
                    y, x = to_check.pop(0)
                    elements.append((x, y))
                    x_sum += x
                    y_sum += y
                    count += 1
                    for ii in range(x - 1, x + 2):
                        for jj in range(y - 1, y + 2):
                            if binarized[jj, ii]:
                                binarized[jj, ii] = False
                                to_check.append((jj, ii))

                x_cord = int(x_sum / count)
                y_cord = int(y_sum / count)
                radius = 0
                for (x, y) in elements:
                    distance = ((x - x_cord) ** 2 + (y - y_cord) ** 2) ** (0.5)
                    radius = max(radius, distance)

                area = (radius ** 2) * 3.14
                shape = find_shape(x_cord, y_cord, radius, area, elements)
                bodies.append(body(len(bodies), x_cord, y_cord, shape))
    return bodies
    
def find_shape(x, y, radius, area, elements):
    fill_area = len(elements)/area
    if fill_area < 0.25:
        return "cross"
    if fill_area < 0.50:
        element_line = []
        for (i, j) in elements:
            if i == x:
                element_line.append(abs(j - y))
        element_line.sort()
        for i in range(1, len(element_line)):
            if element_line[i] - element_line [i - 1] > 1:
                return "spiral"
        return "star"

    if fill_area < 0.83:
        y_min = 10000
        for (i, j) in elements:
            if i == x:
                y_min = min(abs(j - y), y_min)
        if y_min/ radius < 0.3:
            return "flower"
        else:
            return "donut"
    return "circle"

def angle(bodyA, bodyB, bodyC):                                                                              # finds the angle BAC
    angleB = math.atan2((bodyB.y_cord - bodyA.y_cord), (bodyB.x_cord - bodyA.x_cord))
    angleC = math.atan2((bodyC.y_cord - bodyA.y_cord), (bodyC.x_cord - bodyA.x_cord))
    angle = abs(angleB - angleC)
    return min(angle, 2 * math.pi - angle)

def compare_triangles(triangle1, triangle2):                                                                 # returns true if the triangles are identical 

    for i in range(3):
        if not triangle1[i].shape == triangle2[i].shape:
            return False

    for i in range(3):
        angle_dif = abs(angle(triangle1[(i - 1) % 3], triangle1[i], triangle1[(i + 1) % 3]) - angle(triangle2[(i - 1) % 3], triangle2[i], triangle2[(i + 1) % 3]))
        if angle_dif > 0.015:
            return False
    

    lengths1 = []
    lengths2 = []
    for i in range(3):
        for j in range(i + 1, 3):
            lengths1.append(math.hypot(triangle1[i].x_cord - triangle1[j].x_cord, triangle1[i].y_cord - triangle1[j].y_cord))
            lengths2.append(math.hypot(triangle2[i].x_cord - triangle2[j].x_cord, triangle2[i].y_cord - triangle2[j].y_cord))

    lengths1 = np.array(lengths1)
    lengths2 = np.array(lengths2)
    lengths1 /= sum(lengths1)
    lengths2 /= sum(lengths2)

    for i in range(3):
        if abs(lengths1[i] - lengths2[i]) > 0.05:
            return False

    return True



def find_transformation(src_bodies, dst_bodies, star_cord):
    unique = False
    while not unique:
        src_triangle_indexes = random.sample(range(len(src_bodies)), 3)
        src_triangle = [src_bodies[i] for i in src_triangle_indexes]
        unique = True

        for i in range(3):
            tmp_angle = angle(src_triangle[(i - 1) % 3], src_triangle[i], src_triangle[(i + 1) % 3])
            if tmp_angle < 0.5 or tmp_angle >= math.pi / 2:
                unique = False


        for i in range(3):
            for j in range(i + 1, 3):
                tmp_length = math.hypot(src_triangle[i].x_cord -src_triangle[j].x_cord, src_triangle[i].y_cord - src_triangle[j].y_cord)  
                if tmp_length < 200:
                    unique = False
        
        for i in range(len(src_bodies)):
            for j in range(len(src_bodies)):
                for k in range(len(src_bodies)):
                    if not(i == j or j == k or i == k):
                        if not([i, j, k] == src_triangle_indexes):
                            tmp_triangle = [src_bodies[i], src_bodies[j], src_bodies[k]]
                            if compare_triangles(src_triangle, tmp_triangle):
                                unique = False
                                break
                if not unique: break
            if not unique: break
    
    found = False
    for i in range(len(dst_bodies)):
        for j in range(len(dst_bodies)):
            for k in range(len(dst_bodies)):
                if not(i == j or j == k or i == k):
                    dst_triangle = [dst_bodies[i], dst_bodies[j], dst_bodies[k]]
                    if compare_triangles(src_triangle, dst_triangle):
                        found = True
                        found_triangle = dst_triangle
                        break

            if found: break       
        if found: break   
    
    for i in range(3):
        star_cord[i][0] -=  src_triangle[0].x_cord
        star_cord[i][1] -=  src_triangle[0].y_cord

    src_angle = math.atan2((src_triangle[1].y_cord - src_triangle[0].y_cord), (src_triangle[1].x_cord - src_triangle[0].x_cord))
    dst_angle = math.atan2((found_triangle[1].y_cord - found_triangle[0].y_cord), (found_triangle[1].x_cord - found_triangle[0].x_cord))
    rot_angle = dst_angle - src_angle

    src_length = math.hypot(src_triangle[1].y_cord - src_triangle[0].y_cord, src_triangle[1].x_cord - src_triangle[0].x_cord)
    dst_length = math.hypot(found_triangle[1].y_cord - found_triangle[0].y_cord, found_triangle[1].x_cord - found_triangle[0].x_cord)
    scale = dst_length / src_length
    
    for i in range(3):
        star_angle = math.atan2(star_cord[i][1], star_cord[i][0])
        star_dist = math.hypot(star_cord[i][0], star_cord[i][1])

        star_dist *= scale
        star_angle += rot_angle
        star_cord[i][0] =  star_dist * math.cos(star_angle) + found_triangle[0].x_cord
        star_cord[i][1] =  star_dist * math.sin(star_angle) + found_triangle[0].y_cord
    return star_cord
         


if __name__ == "__main__":
    src_path = input()
    dst_path = input()
    star_cord = np.zeros((3,2))
    star_cord[0][0], star_cord[0][1] = input().split()
    star_cord[1][0], star_cord[1][1] = input().split()
    star_cord[2][0], star_cord[2][1] = input().split()

    src_file = Image.open(src_path)
    dst_file = Image.open(dst_path)
    src = np.array(src_file)
    dst = np.array(dst_file)
    
    src_bodies = find_bodies(src)
    dst_bodies = find_bodies(dst)

    for body in src_bodies:
        print (body.x_cord, end = " ")
        print (body.y_cord, end = " ")
    print()
    for body in dst_bodies:
        print (body.x_cord, end = " ")
        print (body.y_cord, end = " ")
    print()

    for body in src_bodies:
        print (body.shape, end = " ")
    print()
    for body in dst_bodies:
        print (body.shape, end = " ")
    print()

    star_cord = find_transformation(src_bodies, dst_bodies, star_cord)
    

    print (int(star_cord[0][0]), end = " ")
    print (int(star_cord[0][1]), end = " ")
    print (int(star_cord[1][0]), end = " ")
    print (int(star_cord[1][1]), end = " ")
    print (int(star_cord[2][0]), end = " ")
    print (int(star_cord[2][1]))