var vm = new  Vue({
    el: '#app' ,
    data:{
        host,
        token: sessionStorage.token || localStorage.token ,
        user_id: sessionStorage.user_id || localStorage.user_id ,
        password: "" ,
        password2: "" ,
        password2_again: "" ,
    },
    methods:{
        change_password: function () {
            // 更改密码逻辑
            axios.put(this.host + '/password/',
                {
                    'password': this.password,
                    'password2': this.password2,
                    'password2_again': this.password2_again
                },
                {
                    headers: {
                        'Authorization': 'JWT ' + this.token   // 在请求头里面添加token
                    },
                    responseType: 'json'
                }
            )
                .then(function (response) {
                    //请求成功之后的逻辑
                    location.href = '/index.html'
                })
                .catch(function (erroe) {
                    //请求失败之后的逻辑
                    // location.href = this.host + '/user_center_pass.html/'
                    location.href = 'www.meiduo.site:8080'
                })
        }
    }
})