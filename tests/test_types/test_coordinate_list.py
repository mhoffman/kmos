

def test_coord_comparison():
    import os.path
    import sys

    sys.path.insert(0,
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..',
            '..',
            'examples'

    ))

    import AB_model
    print(dir(AB_model))
    pt = AB_model.main()

    coord1 = pt.layer_list.generate_coord('a.(1,0,0)')
    coord2 = pt.layer_list.generate_coord('a.(1,0,0)')

    assert coord1==coord2
    assert (coord1!=coord2) == False

if __name__ == '__main__':
    test_coord_comparison()
