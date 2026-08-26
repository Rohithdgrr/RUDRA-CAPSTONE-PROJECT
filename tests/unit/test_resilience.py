from src.core.resilience_index import calculate_ri, grade_for_ri

def test_calculate_ri():
    assert calculate_ri(True,True,True)==100
    assert calculate_ri(False,False,True)==30
    assert calculate_ri(True,False,True)==70
    assert grade_for_ri(95)=="A"
    assert grade_for_ri(73)=="B"
    assert grade_for_ri(0)=="F"
