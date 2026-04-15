import pygame
import random

from BoundingVolumeHierarchy import BoundingVolumeHierarchy
from BoundingVolumeHierarchy import Node
from Primitives import Vec3
from Primitives import Triangle

# Globals

ALL_TRIANGLES_COUNT = 1000
ALL_TRIANGLES = []

BVH_MAX_DEPTH = 10

# Globals, mutable variables class

class Globals:
    bvh: BoundingVolumeHierarchy = None
    visibleDepth: int = 0
    renderMode: int = 0

def main():
    pygame.init()

    screen = pygame.display.set_mode((1920, 1080))
    pygame.display.set_caption("BVH")

    clock = pygame.time.Clock()
    init()

    timer = 0.0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                onKeyPressed(event.key)

        screen.fill("black")
        render(screen)
        pygame.display.flip()

        deltaTime = clock.tick() / 1000

        timer += deltaTime
        if timer >= 1:
            print(f"FPS: {clock.get_fps():.0f}")
            timer = 0

    pygame.quit()

def generateTriangles():
    if len(ALL_TRIANGLES) > 0:
        ALL_TRIANGLES.clear()

    TRI_SIZE = 64 # Max size of a triangle on the screen in pixels
    PADDING = 4 # Padding between frame max size and first triangle point

    width, height = pygame.display.get_window_size()

    for _ in range(ALL_TRIANGLES_COUNT):
        xOffset = random.uniform(PADDING, width - (PADDING + TRI_SIZE))
        yOffset = random.uniform(PADDING, height - (PADDING + TRI_SIZE))

        a = Vec3(random.uniform(0, TRI_SIZE) + xOffset, random.uniform(0, TRI_SIZE) + yOffset, 0)
        b = Vec3(random.uniform(0, TRI_SIZE) + xOffset, random.uniform(0, TRI_SIZE) + yOffset, 0)
        c = Vec3(random.uniform(0, TRI_SIZE) + xOffset, random.uniform(0, TRI_SIZE) + yOffset, 0)

        triangle = Triangle(a, b, c, [random.uniform(64, 255), random.uniform(64, 255), random.uniform(64, 255)])
        ALL_TRIANGLES.append(triangle)

    # Create and build BVH
    Globals.bvh = BoundingVolumeHierarchy(BVH_MAX_DEPTH)
    Globals.bvh.buildBVH(ALL_TRIANGLES)

def init():
    # Generate Triangles
    generateTriangles()

def onKeyPressed(key: int):
    # Regenerate triangles and bvh using R key
    if key == pygame.K_r:
        generateTriangles()
    # BVH depth view control, using keypad +- key
    elif key == pygame.K_KP_PLUS:
        Globals.visibleDepth += 1

        if Globals.visibleDepth > BVH_MAX_DEPTH:
            Globals.visibleDepth = 0

        print(f"Visible Depth: {Globals.visibleDepth}")
    elif key == pygame.K_KP_MINUS:
        Globals.visibleDepth -= 1

        if Globals.visibleDepth < 0:
            Globals.visibleDepth = BVH_MAX_DEPTH

        print(f"Visible Depth: {Globals.visibleDepth}")
    # BVH Nodes render mode
    elif key == pygame.K_KP_1 and Globals.renderMode != 0:
        Globals.renderMode = 0

        print(f"Switched to render mode: {Globals.renderMode}")
    elif key == pygame.K_KP_2 and Globals.renderMode != 1:
        Globals.renderMode = 1

        print(f"Switched to render mode: {Globals.renderMode}")

# Recursively draw each node bounding box, and draw leaf nodes as red
def drawNode(screen: pygame.Surface, node: Node, depth = 0):
    if depth > Globals.visibleDepth or not node:
        return

    color = [255, 0, 0]
    if depth != Globals.visibleDepth and not node.isLeaf():
        luminance = max(0.05, min(0.8, 1 - depth / BVH_MAX_DEPTH)) * 255
        color = [luminance, luminance , luminance]

    bb = node.boundingBox
    pygame.draw.rect(screen, color, [bb.boxMin.x, bb.boxMin.y, bb.boxMax.x - bb.boxMin.x, bb.boxMax.y - bb.boxMin.y],2)

    drawNode(screen, Globals.bvh.nodes[node.childIndex], depth + 1)
    drawNode(screen, Globals.bvh.nodes[node.childIndex + 1], depth + 1)

def render(screen: pygame.Surface):
    # Traverse BVH and highlight hovered triangle
    mousePos = Vec3(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], 0)

    triIdx = Globals.bvh.traverse(ALL_TRIANGLES, mousePos)
    if triIdx != -1:
        tri = ALL_TRIANGLES[triIdx]
        pygame.draw.polygon(screen, "white", [(tri.a.x, tri.a.y), (tri.b.x, tri.b.y), (tri.c.x, tri.c.y)], 0)

    # Render each triangle, and their centroid
    for tri in ALL_TRIANGLES:
        pygame.draw.polygon(screen, tri.color, [(tri.a.x, tri.a.y), (tri.b.x, tri.b.y), (tri.c.x, tri.c.y)], 1)
        pygame.draw.circle(screen, tri.color, (tri.centroid.x, tri.centroid.y), 3)

    if Globals.renderMode == 0: # Recursively draw each node bounding box
        drawNode(screen, Globals.bvh.nodes[0])
    elif Globals.renderMode == 1: # Only draw leaf nodes, in red
        for node in Globals.bvh.nodes:
            if not node.isLeaf():
                continue

            bb = node.boundingBox
            pygame.draw.rect(screen, "red", [bb.boxMin.x, bb.boxMin.y, bb.boxMax.x - bb.boxMin.x, bb.boxMax.y - bb.boxMin.y], 2)

if __name__ == '__main__':
    main()
