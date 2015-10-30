"""
Adjacency matrix

Contact:
Ningchuan Xiao
The Ohio State University
Columbus, OH
"""

__author__ = "Ningchuan Xiao <ncxiao@gmail.com>"

from osgeo import ogr
import numpy as np
import pickle

XMIN = 0  # envelope[0]: xmin
XMAX = 1  # envelope[1]: xmax
YMIN = 2  # envelope[2]: ymin
YMAX = 3  # envelope[3]: ymax

def env_touch(e1, e2):
    """
    Tests if envelopes e1 and e2 touch each other
    """
    if e1[XMAX]<e1[XMIN] or e1[XMIN]>e2[XMAX] or e1[YMAX]<e2[YMIN] or e1[YMIN]>e2[YMAX]:
        return False
    return True

def geom_share(g1, g2, n0):
    """
    Tests if geometry objects g1 and g2 are adjacent

    Input
      g1, g2: OGR geometry objects
      n0: number of points shared for adjacency

    Output
      True/False
    """
    pts1 = []
    if g1 is None or g2 is None:
        return False
    for g in g1:
        if g.GetGeometryCount()>0:
            for gg in g:
                pts1.extend(gg.GetPoints())
        else:
            pts1.extend(g.GetPoints())
    pts2 = []
    for g in g2:
        if g.GetGeometryCount()>0:
            for gg in g:
                pts2.extend(gg.GetPoints())
        else:
            pts2.extend(g.GetPoints())
    np = 0
    for p1 in pts1:
        for p2 in pts2:
            if p1==p2:
                np+=1
            if np>=n0:
                return True
    return False

def adjacency_matrix(shpfname, output="M", num_shared_points=1):
    """
    Creates adjacent matrix based on a polygon shapefile

    Input
      shpfname: the full path of the shapefile, e.g., '/data/uscnty48area.shp'
      output: output format, M - matrix (default), L - list
      num_shared_points: number of shared points required for adjacency

    Output
      The adjacency between polygons in matrix or list form
    """
    driver = ogr.GetDriverByName("ESRI Shapefile")
    vector = driver.Open(shpfname, 0)
    layer = vector.GetLayer(0)
    n = layer.GetFeatureCount()
    if output=="M":
        adj = np.array([[0]*n for x in range(n)])
    elif output=="L":
        adj = []
    else:
        return None
    for i in range(n):
        feature1 = layer.GetFeature(i)
        geom1 = feature1.GetGeometryRef()
        env1 = geom1.GetEnvelope()
        for j in range(i):
            feature2 = layer.GetFeature(j)
            geom2 = feature2.GetGeometryRef()
            env2 = geom2.GetEnvelope()
            if not env_touch(env1, env2):
                continue
            is_adj = False
            if geom1.Touches(geom2):
                if geom_share(geom1, geom2, num_shared_points):
                    is_adj = True
            elif geom1.Contains(geom2):
                is_adj = True
            if is_adj:
                if output=="M":
                    adj[i][j] = adj[j][i] = 1
                elif output=="L":
                    adj.append([i, j])
                else: # undefined
                    pass
    return adj

if __name__ == "__main__":
    shpfname = '../data/uscnty48area.shp'
    shpadj = adjacency_matrix(shpfname)
    pickle.dump(shpadj, open('uscnty48area.adj.pickle', 'w'))
