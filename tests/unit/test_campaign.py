from src.core.campaign import Campaign

def test_campaign_load():
    c = Campaign.from_yaml("campaigns/sensor_suite.yaml")
    assert c.config.name == "Sensor Suite Validation"
    assert len(c.config.faults)==3

def test_campaign_run():
    c = Campaign.from_yaml("campaigns/sensor_suite.yaml")
    res = c.run()
    assert res.total_count==3
    assert 0 <= res.resilience_index <=100
    assert res.grade in "ABCDF"
