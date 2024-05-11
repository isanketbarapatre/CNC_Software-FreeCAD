def generate_json(profile_name="Default Name", note="Generated by step2nulink",
                  customer="", order_number="", dimensions=[0, 0], points=[], line_segments=[],
                  cuts=[], bends=[], radii=[], stamps=[]):
    data = {
        'profile': {
            'name': {
                "de": profile_name,
                "en": profile_name
            },
            'note': note,
            'customer': customer,
            'orderNumber': order_number,
            'geometry': {
                'rotation': {'x': 0, 'y': 0, 'z': 0},
                'version': '1.0',
                'dimensions': {
                    'start': dimensions[0],
                    'end': dimensions[1]
                },
                'units': {'distance': 'mm', 'mass': 'kg', 'area': 'm2'},
                'facing': 'top',
                'points': points,
                'shape': line_segments,
                'cuts': cuts,
                'bends': bends,
                'radii': radii,
                'stamps': stamps,
                'stampingTools': []
            }
        }
    }
    return data
