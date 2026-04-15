# Vec3

def getOther(other):
    if isinstance(other, (int, float)):
        return Vec3(other, other, other)

    return other

class Vec3:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def magnitudeSquared(self):
        for axis in [self.x, self.y, self.z]:
            if axis == float('inf'):
                return float('inf')
            elif axis == float('-inf'):
                return float('-inf')

        return self.x**2 + self.y**2 + self.z**2

    def __add__(self, other):
        other = getOther(other)
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        other = getOther(other)
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __rsub__(self, other):
        other = getOther(other)
        return Vec3(other.x - self.x, other.y - self.y, other.z - self.z)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vec3(self.x * other, self.y * other, self.z * other)

        other = getOther(other)
        return Vec3(self.x * other.x, self.y * other.y, self.z * other.z)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Vec3(self.x / other, self.y / other, self.z / other)

        other = getOther(other)
        return Vec3(self.x / other.x, self.y / other.y, self.z / other.z)

    def __eq__(self, other):
        if isinstance(other, (int, float)):
            other = Vec3(other, other, other)

        return self.x == other.x and self.y == other.y and self.z == other.z

    def __lt__(self, other):
        other = getOther(other)
        return self.magnitudeSquared() < other.magnitudeSquared()

    def __le__(self, other):
        other = getOther(other)
        return self.magnitudeSquared() <= other.magnitudeSquared()

    def __gt__(self, other):
        other = getOther(other)
        return self.magnitudeSquared() > other.magnitudeSquared()

    def __ge__(self, other):
        other = getOther(other)
        return self.magnitudeSquared() >= other.magnitudeSquared()

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z
        else:
            raise IndexError("Vec3 index out of range")

    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index == 2:
            self.z = value
        else:
            raise IndexError("Vec3 index out of range")

    def __str__(self):
        return f'({self.x}, {self.y}, {self.z})'

# Bounding Box Class

class BoundingBox:
    def __init__(self, boxMin = None, boxMax = None):
        self.boxMin = Vec3(float('inf'), float('inf'), float('inf')) if boxMin is None else boxMin
        self.boxMax = Vec3(float('-inf'), float('-inf'), float('-inf')) if boxMax is None else boxMax

        self.size = Vec3(0, 0, 0)
        self.center = Vec3(0, 0, 0)
        self.updateSizeAndCenter()

    def updateSizeAndCenter(self):
        self.size = self.boxMax - self.boxMin
        self.center = self.boxMin + self.size * 0.5

    def intersect(self, pos: Vec3):
        aboveMin = pos.x >= self.boxMin.x and pos.y >= self.boxMin.y and pos.z >= self.boxMin.z
        belowMax = pos.x <= self.boxMax.x and pos.y <= self.boxMax.y and pos.z <= self.boxMax.z

        return aboveMin and belowMax

# Triangle Class

def sign(p1: Vec3, p2: Vec3, p3: Vec3):
    return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)

class Triangle:
    def __init__(self, a: Vec3, b: Vec3, c: Vec3, color):
        self.a = a
        self.b = b
        self.c = c

        self.centroid = (a + b + c) / 3.0
        self.minPos = Vec3(
            min(a.x, b.x, c.x),
            min(a.y, b.y, c.y),
            min(a.z, b.z, c.z)
        )
        self.maxPos = Vec3(
            max(a.x, b.x, c.x),
            max(a.y, b.y, c.y),
            max(a.z, b.z, c.z)
        )

        self.color = color

    # Thanks to https://stackoverflow.com/questions/2049582/how-to-determine-if-a-point-is-in-a-2d-triangle
    def intersect(self, pos: Vec3):
        d1 = sign(pos, self.a, self.b)
        d2 = sign(pos, self.b, self.c)
        d3 = sign(pos, self.c, self.a)

        hasNeg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        hasPos = (d1 > 0) or (d2 > 0) or (d3 > 0)

        return not (hasNeg and hasPos)