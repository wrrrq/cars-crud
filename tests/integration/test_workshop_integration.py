from app import database
from app.schemas import CarInput

def test_saved_car_can_be_read_from_sqlite(database_path):
    database.initialize(database_path)
    saved = database.create_car(
        database_path,
        CarInput(make="Toyota", model="Yaris", year=2020, color="Blue"),
    )
    loaded = database.get_car(database_path, saved.id)
    assert loaded is not None
    assert loaded.id == saved.id
    assert loaded.make == "Toyota"
    assert loaded.year == 2020

def test_deleting_one_car_keeps_the_other(database_path):
    database.initialize(database_path)
    
    car1 = database.create_car(database_path, CarInput(make="Toyota", model="Corolla", year=2020, color="White"))
    car2 = database.create_car(database_path, CarInput(make="Honda", model="Civic", year=2022, color="Black"))
    
    database.delete_car(database_path, car1.id)
    
    # 断言第一辆车被删除了
    assert database.get_car(database_path, car1.id) is None
    
    # 断言第二辆车还在
    loaded_car2 = database.get_car(database_path, car2.id)
    assert loaded_car2 is not None
    assert loaded_car2.id == car2.id
    
    # 断言列表里只有第二辆车
    all_cars = database.list_cars(database_path)
    assert len(all_cars) == 1
    assert all_cars[0].id == car2.id