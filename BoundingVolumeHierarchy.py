from typing import List

from Primitives import Vec3
from Primitives import BoundingBox
from Primitives import Triangle

class Node:
    def __init__(self, boundingBox = None):
        self.boundingBox = BoundingBox() if boundingBox is None else boundingBox

        self.childIndex = 0 # Left child index, +1 to get right child index
        self.triIndex = 0
        self.triCount = 0

    def growToInclude(self, tri: Triangle):
        self.boundingBox.boxMin.x = min(self.boundingBox.boxMin.x, tri.minPos.x)
        self.boundingBox.boxMin.y = min(self.boundingBox.boxMin.y, tri.minPos.y)
        self.boundingBox.boxMin.z = min(self.boundingBox.boxMin.z, tri.minPos.z)

        self.boundingBox.boxMax.x = max(self.boundingBox.boxMax.x, tri.maxPos.x)
        self.boundingBox.boxMax.y = max(self.boundingBox.boxMax.y, tri.maxPos.y)
        self.boundingBox.boxMax.z = max(self.boundingBox.boxMax.z, tri.maxPos.z)

        self.boundingBox.updateSizeAndCenter()

    def isLeaf(self):
        return self.childIndex == 0

class BoundingVolumeHierarchy:
    def __init__(self, maxDepth: int):
        self.nodes = []
        self.maxDepth = maxDepth

    def buildBVH(self, TRIANGLES: List[Triangle]):
        rootNode = Node()
        rootNode.triCount = len(TRIANGLES)

        for i in range(rootNode.triCount):
            rootNode.growToInclude(TRIANGLES[rootNode.triIndex + i])

        self.nodes.append(rootNode)
        self.split(TRIANGLES, rootNode, 0)

    # Determines split pos using midpoint split
    def chooseSplit(self, node: Node):
        boundingBox = node.boundingBox
        size = boundingBox.size

        splitAxis = 0 if size.x > max(size.y, size.z) else 1 if size.y > size.z else 2
        splitPos = boundingBox.center[splitAxis]

        return splitAxis, splitPos

    # Recursively split parent node into 2 child node until maxDepth is reached or triangle count is <= 2
    # Also sort triangles into a continuous block, to later be sent to the GPU
    def split(self, TRIANGLES: List[Triangle], parent: Node, currentDepth: int):
        if currentDepth >= self.maxDepth or parent.triCount <= 2:
            return

        splitAxis, splitPos = self.chooseSplit(parent)
        parent.childIndex = len(self.nodes)

        nodeA = Node()
        nodeA.triIndex = parent.triIndex

        nodeB = Node()
        nodeB.triIndex = parent.triIndex

        self.nodes.append(nodeA)
        self.nodes.append(nodeB)

        for i in range(parent.triCount):
            triIdx = parent.triIndex + i
            tri = TRIANGLES[triIdx]

            inSideA = tri.centroid[splitAxis] < splitPos
            child = nodeA if inSideA else nodeB
            child.growToInclude(tri)
            child.triCount += 1

            if inSideA:
                swapIndex = child.triIndex + child.triCount - 1

                TRIANGLES[triIdx] = TRIANGLES[swapIndex]
                TRIANGLES[swapIndex] = tri

                nodeB.triIndex += 1

        self.split(TRIANGLES, nodeA, currentDepth + 1)
        self.split(TRIANGLES, nodeB, currentDepth + 1)

    # GPU friendly traverse bvh method
    # If you want to write this in GLSL, use an index pointer instead of the fancy python's pop method
    def traverse(self, TRIANGLES: List[Triangle], pos: Vec3):
        stack = [self.nodes[0]]
        result = -1

        while stack:
            node = stack.pop()

            if not node.boundingBox.intersect(pos):
                continue

            if node.isLeaf():
                for i in range(node.triCount):
                    triIdx = node.triIndex + i

                    if TRIANGLES[triIdx].intersect(pos):
                        result = triIdx
                        break # In case of a raytracer, you would want to keep track of the closest triangle here. Do NOT break the loop!
            else:
                stack.append(self.nodes[node.childIndex + 1])
                stack.append(self.nodes[node.childIndex])

        return result
