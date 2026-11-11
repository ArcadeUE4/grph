from PyQt6.QtCore import QPointF

class CurveAlgorithms:
    """Алгоритмы расчета кривых."""
    @staticmethod
    def computeDeCasteljauPyramid(points, t):
        """Пирамида промежуточных точек де Кастельжо."""
        pyramid = [points]
        while len(pyramid[-1]) > 1:
            currentLevel = pyramid[-1]
            nextLevel = []
            for i in range(len(currentLevel) - 1):
                x = (1.0 - t) * currentLevel[i].x() + t * currentLevel[i + 1].x()
                y = (1.0 - t) * currentLevel[i].y() + t * currentLevel[i + 1].y()
                nextLevel.append(QPointF(x, y))
            pyramid.append(nextLevel)
        return pyramid

    @staticmethod
    def computeBezierPoints(points, segments=120):
        """Построение гладкой кривой Безье."""
        if len(points) < 2:
            return []
        curvePoints = []
        for step in range(segments + 1):
            t = step / segments
            tempPoints = list(points)
            while len(tempPoints) > 1:
                tempPoints = [
                    QPointF(
                        (1.0 - t) * tempPoints[i].x() + t * tempPoints[i + 1].x(),
                        (1.0 - t) * tempPoints[i].y() + t * tempPoints[i + 1].y()
                    )
                    for i in range(len(tempPoints) - 1)
                ]
            curvePoints.append(tempPoints[0])
        return curvePoints

    @staticmethod
    def computeChaikinPoints(points, iterations):
        """Алгоритм Чайкина со срезанием углов (в пропорциях 1/4 и 3/4)."""
        polygon = list(points)
        for _ in range(iterations):
            if len(polygon) < 2:
                break
            refined = [polygon[0]]
            for i in range(len(polygon) - 1):
                p0 = polygon[i]
                p1 = polygon[i + 1]

                qx = 0.75 * p0.x() + 0.25 * p1.x()
                qy = 0.75 * p0.y() + 0.25 * p1.y()

                rx = 0.25 * p0.x() + 0.75 * p1.x()
                ry = 0.25 * p0.y() + 0.75 * p1.y()

                refined.append(QPointF(qx, qy))
                refined.append(QPointF(rx, ry))
            refined.append(polygon[-1])
            polygon = refined
        return polygon
