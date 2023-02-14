let app1 = new Vue({
  el: "#user_sess",
  delimiters: ["{", "}"],
  data: {
    user_name: false,
    email: false,
  },
  methods: {
    init: function() {
        this.get_user_data();
    },
    get_user_data: function(page) {
      const csrftoken = Cookies.get('csrftoken');
      axios.post("/get_user_session_data/", {
        'Accept': 'application/json',
        headers: {'X-CSRFToken': csrftoken},
        
      }).then(async response => {
        const data = await response.data;
        all_data = JSON.parse(data)
        this.user_name = all_data['username']
        this.email = all_data['email']
        
      });
    },
  },
  mounted: function () {
    this.init();
  }
})