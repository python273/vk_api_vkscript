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
