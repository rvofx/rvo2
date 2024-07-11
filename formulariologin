import streamlit as st

# Lista de usuarios y contraseñas
usuarios = {
    'rvo': '1234',
    'abc': '5678'
}

st.title('Inicio de Sesión')

username = st.text_input('Usuario')
password = st.text_input('Contraseña', type='password')

if st.button('Iniciar Sesión'):
    if username in usuarios and usuarios[username] == password:
        st.success('Inicio de sesión exitoso')
    else:
        st.error('Usuario o contraseña incorrectos')
