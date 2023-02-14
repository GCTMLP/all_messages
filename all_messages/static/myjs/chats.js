let app = new Vue({

  el: "#chats",
  delimiters: ["{", "}"],
  data: {
    request: false,
    chats: {},
    messages: {},
    text: null,
    checkedMess: [],
    bigname: 'Choose chat',
    comment: 'Choose chat',
    user_id: null,
    now_connection: 0,
    add: {
    name: null,
    comment: null,
    phones: null,
    show_send:0,

    }

  },
  methods: {
    init: function() {
        this.left_chats()

    },


    left_chats() {
            let self = this
            console.log("connected to ch")
            const currentUrl = window.location.host;
            this.connection = new WebSocket("ws://"+currentUrl+"/ws/chat/left_chat")

            console.log(this.connection)
            this.connection.onmessage = function(event) {
              const all_data = JSON.parse(event.data);
              self.chats = all_data
              console.log(self.chats)
            }

            this.connection.onopen = function(event) {
              console.log(event)
              console.log("Successfully connected to the echo websocket server...")
            }

          },

    created(id, name) {
        let self = this
        const currentUrl = window.location.host;
        if  (self.now_connection == 0){

            self.now_connection = new WebSocket("ws://"+currentUrl+"/ws/chat/"+id)
            self.show_send = 1
        }
        else{
            self.now_connection.close()
            self.now_connection = new WebSocket("ws://"+currentUrl+"/ws/chat/"+id)
        }

        console.log(this.connection)
        self.now_connection.onmessage = function(event) {
          self.chats[name]['new'] = 0
          const all_data = JSON.parse(event.data);
          self.connected_ws = id
          self.messages = all_data['messages']
          self.bigname = all_data['name']
          self.comment = all_data['comment']
        }

        self.now_connection.onopen = function(event) {
          console.log(event)
          console.log("Successfully connected to the echo websocket server...")
        }

      },

      send_message() {
        let self = this
        data = {
          text:self.text,
          mess:self.checkedMess,
        }
        self.now_connection.send(JSON.stringify(data))

      },

  },
  mounted: function () {
    this.init();
  }
})

