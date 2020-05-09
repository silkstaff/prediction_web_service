var position = "{{ session['login'] }}"

if (position == "YES"){
    alert('이미 로그인된 상태입니다.');
    window.location='/'
}