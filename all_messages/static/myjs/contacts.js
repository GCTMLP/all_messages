let app = new Vue({
  
  el: "#contacts",
  delimiters: ["{", "}"],
  data: {
    request: false,
    contacts: {},
    filter: {
      page: 1,
      limit: 5,
      pages_big: 0,
      search: '',
    },
    add: {
    name: null,
    comment: null,
    phones: null
    }
  },
  methods: { 
    init: function() {
        this.get_contacts(this.filter.page);

    },
    get_contacts: function(page) {
          const params = {
            page: page,
            limit: this.filter.limit,
            search: this.filter.search
          };
          axios.post("get_all_contacts/", params, {
            'Accept': 'application/json'

          }).then(async response => {
            const data = await response.data;
            all_data = JSON.parse(data)
            this.contacts = all_data['data']
            q_count = all_data['count']
            this.filter.pages = Math.floor(q_count / this.filter.limit);
            if(q_count % this.filter.limit != 0){
              this.filter.pages += 1
            }
          });
    },
    save_change(id){
        console.log(id)
        console.log(this.contacts[id].name)
        data_change = {
            id: id,
            name:this.contacts[id].name,
            comment:this.contacts[id].comment
        };
        axios.post("change_contact_info/", data_change, {
        'Accept': 'application/json'
        }).then(async response => {
        const data = await response.data;
        if (data == 'True'){
          this.$toastr.defaultTimeout = 3000;
          this.$toastr.defaultPosition = "toast-top-right";
          this.$toastr.defaultStyle = { "background-color": "green" },
          this.$toastr.s("Save changes");
          this.init()
          this.a_text = null
        }
        else{
          this.$toastr.defaultTimeout = 3000;
          this.$toastr.defaultPosition = "toast-top-right";
          this.$toastr.defaultStyle = { "background-color": "red" },
          this.$toastr.s("Errors in saving");
        }
      });
    },

    delete_contact(id){
        data_change = {
            id: id,
        };
        axios.post("delete_contact_info/", data_change, {
        'Accept': 'application/json'
        }).then(async response => {
        const data = await response.data;
        if (data == 'True'){
          this.init();
          this.$toastr.defaultTimeout = 3000;
          this.$toastr.defaultPosition = "toast-top-right";
          this.$toastr.defaultStyle = { "background-color": "green" },
          this.$toastr.s("Deleted");
          this.init()
          this.a_text = null
        }
        else{
          this.$toastr.defaultTimeout = 3000;
          this.$toastr.defaultPosition = "toast-top-right";
          this.$toastr.defaultStyle = { "background-color": "red" },
          this.$toastr.s("Errors in deleting");
        }
      });
    },

    add_contact(){
        data_add = {
            name: this.add.name,
            comment: this.add.comment,
            phones: this.add.phones,
        };
        axios.post("add_contact_info/", data_add, {
            'Accept': 'application/json'
            }).then(async response => {
            const data = await response.data;
            if (data == 'True'){
              this.init();
              this.$toastr.defaultTimeout = 3000;
              this.$toastr.defaultPosition = "toast-top-right";
              this.$toastr.defaultStyle = { "background-color": "green" },
              this.$toastr.s("Added _ contact");
              this.init()
              this.a_text = null
            }
            else{
              this.$toastr.defaultTimeout = 3000;
              this.$toastr.defaultPosition = "toast-top-right";
              this.$toastr.defaultStyle = { "background-color": "red" },
              this.$toastr.s("Errors in adding");
            }
      });

    },

    // PAGINATION
    minus_page: function(){
      if (this.filter.page % 5 == 0 && this.filter.pages_big+1 == this.filter.page){
        this.filter.pages_big-=4
        this.filter.page = this.filter.page-=1
      }
      else{
        this.filter.page = this.filter.page-=1
      }
      if(this.filter.page % 5 == 0 ){
        this.filter.pages_big-=4
      }
      this.get_questions(this.filter.page)
    },

    plus_page: function(){
      if (this.filter.page % 5 == 0 && this.filter.pages_big+5 == this.filter.page){
        this.filter.pages_big+=4
        this.filter.page = this.filter.page+=1
      }
      else{
        this.filter.page = this.filter.page+=1
      }
      if(this.filter.page % 5 == 0){
        this.filter.pages_big+=4
      }
      this.get_questions(this.filter.page)
    },

    change_page_big: function(page_chosen){
      if(page_chosen % 5 == 0 && page_chosen > this.filter.page){
        this.filter.pages_big+=4
      }
      if(page_chosen % 5 == 0 && page_chosen < this.filter.page){
        this.filter.pages_big-=4
      }
      this.filter.page = page_chosen
      this.get_questions(this.filter.page)
    },
    change_count: function(limit){
      this.filter.limit = limit
      this.filter.page = 1
      this.get_questions(this.filter.page);
    },
    clean_search: function(){
      this.filter.search = null
      this.get_questions(1)
    },

  },
  mounted: function () {
  this.init();
  }
})

