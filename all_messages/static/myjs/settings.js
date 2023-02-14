let app = new Vue({
  el: "#settings",
  delimiters: ["{", "}"],
  data: {
    login: null,
    foto: null,
    file: null,
    email: null,
    request: false,
    enter_code_1: 1,
    enter_code_2: 1,
    tg_code:null,
    show_tg_connection:0,
    show_tg_reconnection:1,
    user_data:{
        f_name: null,
        s_name: null,
        email:null,
        location: null,
        username: null
    },
    connect_api_data:{
        phone_number:null,
        app_id:null,
        token:null
    },
    visible: true,
    settings: {},
    styleObject: {
      width: '118px',
      height: '118px',
      background: this.foto,
    },
  },

  methods: {
    init: function() {
        this.get_settings();
    },
    get_settings: function() {
      axios.post("get_settings/", {
        'Accept': 'application/json'
        
      }).then(async response => {
        const data = await response.data;
        all_data = JSON.parse(data)
        console.log(all_data)
        this.user_data.f_name = all_data['user_data']['name'],
        this.user_data.s_name=all_data['user_data']['surname'],
        this.user_data.email=all_data['user_data']['email'],
        this.user_data.location=all_data['user_data']['location'],
        this.user_data.username=all_data['user_data']['user_name'],

        this.connect_api_data.phone_number=all_data['tg_settings']['phone'],
        this.connect_api_data.app_id=all_data['tg_settings']['app_id'],
        this.connect_api_data.token=all_data['tg_settings']['token'];
        if (this.connect_api_data.phone_number != null){
            this.show_tg_connection=1,
            this.show_tg_reconnection=0;
            }
      });
    },

    change_user_data(){

        data = {
            'f_name':this.user_data.f_name,
            's_name':this.user_data.s_name,
            'email':this.user_data.email,
            'location':this.user_data.location,
            'username':this.user_data.username
        },
        axios.post("change_user_data/", data, {
        'Accept': 'application/json'

      }).then(async response => {
        const data = await response.data;
        if (data == 'true'){
              this.$toastr.defaultTimeout = 3000;
              this.$toastr.defaultPosition = "toast-top-right";
              this.$toastr.defaultStyle = { "background-color": "green" };
              this.$toastr.s("User data changed successfully");
              this.show_tg_connection=1;
              this.show_tg_reconnection=0;
            }
            else{
              this.$toastr.defaultTimeout = 3000;
              this.$toastr.defaultPosition = "toast-top-right";
              this.$toastr.defaultStyle = { "background-color": "red" },
              this.$toastr.s("Errors in changing user data");
            }
      });

    },

    connect_api(messenger){
        this.enter_code_1 = 0
        data_request = {
            messenger: messenger,
            phone: this.connect_api_data.phone_number,
            app_id: this.connect_api_data.app_id,
            token: this.connect_api_data.token
        },
        axios.post("register_api/", data_request, {
        'Accept': 'application/json'
        }).then(async response => {
            const data = await response.data;
            console.log(data)
             if (data == 'true'){
              this.$toastr.defaultTimeout = 3000;
              this.$toastr.defaultPosition = "toast-top-right";
              this.$toastr.defaultStyle = { "background-color": "green" };
              this.$toastr.s("Telegram account connected successfully");
              this.show_tg_connection=1;
              this.show_tg_reconnection=1;
            }
            else{
              this.$toastr.defaultTimeout = 3000;
              this.$toastr.defaultPosition = "toast-top-right";
              this.$toastr.defaultStyle = { "background-color": "red" },
              this.$toastr.s("Errors in connecting telegram account");
            }
          });
    },

    send_tg_code(code_n){
        if (code_n == 1){
            this.enter_code_1 = 1;
            this.enter_code_2 = 0;
        }
        data_request = {
            tr:code_n,
            tg_code: this.tg_code,
            phone: this.connect_api_data.phone_number,
            app_id: this.connect_api_data.app_id,
            token: this.connect_api_data.token
        },
        axios.post("write_tg_code/", data_request, {
        'Accept': 'application/json'
        }).then(async response => {
            const data = await response.data;
            all_data = JSON.parse(data)
         });
    },

    hide_foto(){
      this.visible = false
      this.file = this.$refs.file.files[0];
    },
      

  },
  mounted: function () {
    this.init();
  }
})