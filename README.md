# vk_api_vkscript

A little experiment with transpilation of python function code
 into [VKScript](https://vk.com/dev/execute)

```python
import vk_api
from parser import vkscript, API, parseInt

@vkscript
def inc_status(vk):
    x = parseInt(API.status.get()['text'])
    x = x + 1
    return API.status.set(text=x)

vk_session = vk_api.VkApi('python@vk.com', 'mypassword')
vk_session.auth(token_only=True)
vk = vk_session.get_api()
print(inc_status(vk))
```

`inc_status` fn has 2 calls to API, but after applying `vkscript` decorator
 it gets converted into VKScript function, so only one `execute` call being
 made when calling it (`inc_status(vk)`)

```js
var x = parseInt(API.status.get()["text"]);
x = x + 1;
return API.status.set({text:x});
```
