from models.Usuario import UsuarioModel
try:
    result = UsuarioModel.autenticar('admin', '123')
    print(f'Login succeeded: {result is not None}')
    if result:
        print(f"User: {result['nome']}")
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
