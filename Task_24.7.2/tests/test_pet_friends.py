import os
from api import PetFriends
from settings import (valid_email,
                      valid_password,
                      not_valid_email,
                      not_valid_password)


pf = PetFriends()


def test_get_api_key_for_valid_user(
    email = valid_email,
    password = valid_password
):
    """Проверяем, что запрос API ключа возвращает статус 200 и в результате содержится слово key"""
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert 'key' in result


def test_get_api_key_for_not_valid_email_and_password(
    email = not_valid_email,
    password = not_valid_password
):
    """Проверяем, что запрос API ключа с неверными данными пользователя возвращает статус 403
    и в результате не содержится слово key"""
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result


def test_get_all_pets_with_valid_key(filter=''):
    """Проверяем, что запрос списка всех питомцев возвращает не пустой список"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(
    name='Красава',
    animal_type='Котей',
    age='1',
    pet_photo_path='images/cat_01.jpg'
):
    """Проверяем, что запрос на добавление нового питомца с указанными параметрами выполняется успешно"""
    pet_photo_path = os.path.join(os.path.dirname(__file__), pet_photo_path)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(
        auth_key,
        name,
        animal_type,
        age,
        pet_photo_path
    )

    assert status == 200
    assert result['name'] == name
    assert result['animal_type'] == animal_type


def test_add_new_pet_with_empty_age(
    name='Милашка',
    animal_type='',
    age='2',
    pet_photo_path='images/dog_01.jpg'
):
    """Проверяем, что запрос на добавление нового питомца с пустым полем порода выполняется успешно"""
    pet_photo_path = os.path.join(os.path.dirname(__file__), pet_photo_path)

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(
        auth_key,
        name,
        animal_type,
        age,
        pet_photo_path
    )

    assert status == 200
    assert 'name' in result


def test_add_new_pet_with_negative_age(
    name='Хитрюха',
    animal_type='Котофей',
    age='-10',
    pet_photo_path='images/cat_02.jpg'
):
    """Проверяем, что запрос на добавление нового питомца с отрицательным возрастом выполняется успешно"""
    pet_photo_path = os.path.join(os.path.dirname(__file__), pet_photo_path)

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(
        auth_key,
        name,
        animal_type,
        age,
        pet_photo_path
    )

    assert status == 200
    assert 'name' in result


def test_add_new_pet_with_space_in_age(
        name='Ромашка',
        animal_type='100500',
        age='3',
        pet_photo_path='images/dog_02.jpg'
):
    """Проверяем, что запрос на добавление нового питомца с некорректным параметром поля порода выполняется успешно"""
    pet_photo_path = os.path.join(os.path.dirname(__file__), pet_photo_path)

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(
        auth_key,
        name,
        animal_type,
        age,
        pet_photo_path
    )

    assert status == 200
    assert 'name' in result


def test_add_new_pet_with_incorrect_age(
    name='Пафнутий',
    animal_type='Садовый кот',
    age='стольконеживут',
    pet_photo_path='images/cat_03.jpg'
):
    """Проверяем, что запрос на добавление питомца с некорректным параметром возраст выполняется успешно"""
    pet_photo_path = os.path.join(os.path.dirname(__file__), pet_photo_path)

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(
        auth_key,
        name,
        animal_type,
        age,
        pet_photo_path
    )

    assert status == 200
    assert result['name'] == name
    assert result['age'] == age


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца.
    Если список питомцев пустой, то добавляем нового питомца и запрашиваем список своих питомцев"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, pf.MY_PETS)

    if not my_pets['pets']:
        pf.add_new_pet(auth_key, "Соня", "Спаниэль", "3", "images/dog_03.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, pf.MY_PETS)

    # Берём ID последнего добавленного питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, pf.MY_PETS)

    # Проверяем что статус ответа равен 200 и в списке питомцев нет ID удалённого питомца
    assert status == 200
    assert pet_id not in [pet['id'] for pet in my_pets['pets']]


def test_successful_update_self_pet_info(
    name='Красавчик',
    animal_type='Котейка',
    age='2'
):
    """Проверяем возможность обновления информации о первом добавленном питомце с некорректными параметрами"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, pf.MY_PETS)
    if not my_pets['pets']:
        raise Exception("There is no my pets")
    pet_id = my_pets['pets'][-1]['id']

    status, result = pf.update_pet_info(auth_key,
        pet_id,
        name,
        animal_type,
        age
    )

    # Проверяем что статус ответа = 200 и атрибуты питомца поменялись
    assert status == 200
    assert result['name'] == name
    assert result['animal_type'] == animal_type
    assert result['age'] == str(age)
