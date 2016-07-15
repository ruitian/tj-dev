#tj-dev

##Development with virtualenv

install dependent packages
```
pip install -r requirements.txt
```

Init database
```
python run.py upgrade
```

redis
```
redis-server
```

run
```
python run.py runserver
```

可以准备两台虚拟机进行测试，需要将docker进行一下配置，允许api登录，端口改为5678
