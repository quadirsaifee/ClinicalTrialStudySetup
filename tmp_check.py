import importlib
m = importlib.import_module('langchain.agents')
print(m.__file__)
print('has_create_deep_agent=', hasattr(m, 'create_deep_agent'))
print([n for n in dir(m) if 'deep' in n.lower()][:30])
