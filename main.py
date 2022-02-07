import argparse
import copy
from collections import defaultdict

from pbstream.reader import PBstream_Reader

import open3d as o3d

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action', choices=['info', 'trajectory'],
        help='action "info" prints some information about the map, "trajectory" plots the trajectory '
    )
    parser.add_argument('--inputfile', type=str)
    ARGS = parser.parse_args()

    if ARGS.action == 'info':
        PBstream_Reader.info(ARGS.inputfile)
    elif ARGS.action == 'trajectory':
        loaded = defaultdict(list)
        with PBstream_Reader(ARGS.inputfile) as reader:
            for msg in reader:
                fields = msg.ListFields()
                if len(fields) == 0:
                    continue
                for (field_descriptor, message) in fields:
                    loaded[field_descriptor.name].append(message)

        def get_trans_rot(p):
            mesh = o3d.geometry.TriangleMesh.create_coordinate_frame()
            return (p.translation.x, p.translation.y, p.translation.z), mesh.get_rotation_matrix_from_quaternion(
                (p.rotation.w, p.rotation.x, p.rotation.y, p.rotation.z))

        # adding Visualizer
        points, segments = [], []
        vis = o3d.visualization.Visualizer()
        vis.create_window()
        for i, map in enumerate(loaded['pose_graph'][0].trajectory[0].submap):
            mesh = o3d.geometry.TriangleMesh.create_coordinate_frame(size=5 if i == 0 else 3)
            trans_xyz, rotate_wxyz = get_trans_rot(map.pose)
            points.append(trans_xyz)
            if len(points) > 1:
                segments.append([i-1, i])
            mesh.translate(trans_xyz)
            mesh.rotate(rotate_wxyz)

            vis.add_geometry(mesh)

        colors = [[0, 0, 0]] * len(points)

        line_set = o3d.geometry.LineSet()
        line_set.points = o3d.utility.Vector3dVector(points)
        line_set.lines = o3d.utility.Vector2iVector(segments)
        line_set.colors = o3d.utility.Vector3dVector(colors)
        vis.add_geometry(line_set)
        vis.run()
