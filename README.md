# IMG_api

Для тестирования функциональности использовался готовый инструмент для отправки curl запросов: 
Insomnia - https://insomnia.rest/download

База данных состоит из 2х таблиц: таблицы изображений и таблицы тегов.

Таблица изображений содержит в себе имя файла и само изображение. 

SQL строка инициализации:
~~~
CREATE TABLE images ( img_id serial PRIMARY KEY, img_name VARCHAR(20) NOT NULL,img BYTEA);
~~~

Таблица тегов содержит в себе список всех тегов и ID изображений, соответствующих этим тегам.

SQL строка инициализации:
~~~
CREATE TABLE tags ( tag varchar(20) PRIMARY KEY, pictures_id integer[]);
~~~

####Описание основных функций:

#####1)Загрузка изображения

    Вид запроса:
    curl --request PUT --url http://127.0.0.1:5000/image-api/ --header 'Content-Type: application/json' \
      --data '{
                "img_path": "E:/api_pics/img_samples/free_sample2.png",
                "tags": ["test1","test2","test4"]
              }'
    
    Входные параметры:
    img_path - путь до загружаемого изображения
    tags - теги, присваевыемые изображению
    Резуьтат работы:
    В таблице images создается запись содержащая имя изображения и само изображение, в 
    таблице tags к каждому тегу приписывается id текущего изображения, если тега не существует, то создается 
    новый  и ему приписывается id текущего изображения
    
    
#####2)Удаление изображения

    Вид запроса:
    curl --request DELETE --url http://127.0.0.1:5000/image-api/ --header 'Content-Type: application/json' \
      --data '{
                "img_id": 39
             }'
    
    Входные параметры:
    img_id - id удаляемого изображения
    Резуьтат работы:
    Изображение по указанному id удаляется из таблицы images, так же из таблицы тегов из всех записей удаляется id принадлежащее этому изображению

#####3)Редактирование изображения

    Вид запроса:
    curl --request POST --url http://127.0.0.1:5000/image-api/ --header 'Content-Type: application/json' \
      --data '{
                "img_id": 44,
                "img_path": "E:/api_pics/img_samples/free_sample1.png"
             }'
    
    Входные параметры:
    img_id - id изменяемого изображения
    img_path - путь до нового изображения
    Резуьтат работы:
    Изображение по указанному id заменяется на изображение, располагающеея по пути из img_path

#####4)Просмотр списка изображений

    Вид запроса:
    curl --request POST --url http://127.0.0.1:5000/image-api/get_all_images_list
    
    Резуьтат работы:
    Функция возвращает json со списком изображений, их id и их тегами. 
    Результат имеет следующий вид:
    {
        'id': 44, 
        'name': 'free_sample1.png', 
        'tags': ['test2', 'test4', 'test1']
    }
    {
        'id': 45, 
        'name': 'free_sample2.png', 
        'tags': ['test1', 'test3', 'test21']
    }
    {
        'id': 46, 
        'name': 'free_sample2.png', 
        'tags': ['test44', 'test31', 'test21']
    }
    
#####5)Скачивание изображения

    Вид запроса:
    curl --request POST --url http://127.0.0.1:5000/image-api/download_by_id --header 'Content-Type: application/json' \
      --data '{
                "img_id": 4,
                "save_path": "D:/test_dir"
              }'
    
    Входные параметры:
    img_id - id скачиваемого изображения
    save_path - путь куда будет  скачан файл
    Резуьтат работы:
    Изображение с указанным id скачивается на локальную машину в указанный в save_path путь

#####6)Добавление тегов к изображению

    Вид запроса:
    curl --request POST --url http://127.0.0.1:5000/image-api/add_tag_to_image --header 'Content-Type: application/json' \
      --data '{
                "img_id": 42,
                "tag": "test5"
              }'
    
    Входные параметры:
    img_id - id изменяемого изображения
    tag - добавляемый изображению тег
    Резуьтат работы:
    В случае если тег существовал, то в pictures_id, соответствующей этому тегу, добавляется id изображения.
    Если же такого тега нет, то создается новая запись c этим тегом и заполняется pictures_id.
    
#####7)Удаление тегов у изображения
    Вид запроса:
    curl --request POST --url http://127.0.0.1:5000/image-api/delete_tag_from_image --header 'Content-Type: application/json' \
      --data '{
                "img_id": 38,
                "tag": "test1"
              }'
    
    Входные параметры:
    img_id - id изменяемого изображения
    tag - удаляемый у изображения тег
    Резуьтат работы:
    В таблице tags в pictures_id, соответствующей этому тегу, удаляется id изображения.
    
#####8)Просмотр списка изображений осфильтрованных по тегам 

    Вид запроса:
    curl --request POST --url http://127.0.0.1:5000/image-api/filter_by_tags --header 'Content-Type: application/json' \
      --data '{
                "tags": ["test21"]
              }'
    
    Входные параметры:
    tags - теги по которым происходит фильтрация
    Резуьтат работы:
    Функция возвращает id изображений, которые попадают под заданный фильтр.
    Пример вывода для данного фильтра - 45 46
    


