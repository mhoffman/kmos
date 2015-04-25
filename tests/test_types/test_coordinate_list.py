

def test_coord_comparison():

    from kmos.types import Project

    pt = Project()
    pt.import_xml_file('AB_model.xml')

    coord1 = pt.layer_list.generate_coord('a.(1,0,0)')
    coord2 = pt.layer_list.generate_coord('a.(1,0,0)')

    assert coord1==coord2
    assert (coord1!=coord2) == False

if __name__ == '__main__':
    test_coord_comparison()
