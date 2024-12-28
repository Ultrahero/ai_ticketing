<template>
    <v-card>
      <v-card-title>Signup!</v-card-title>

        <v-container v-if="userStore.session_id" class="ma-0 pa-0">
            <v-card-text class="py-0">
                Hoops! It seems you are logged in!
            </v-card-text>
            <v-card-actions class="d-flex flex-column align-center">
                <v-btn @click="handleLogout" v-if="userStore.session_id" block>Logout</v-btn>
            </v-card-actions>
        </v-container>
      
        <v-container v-else class="ma-0 pa-0">
            <v-card-text class="py-0">
                <p>Sign up for amazing features!</p>
                <v-text-field v-model="_username" placeholder="Your Name" label="Username" density="compact"/>
                <v-text-field v-model="_password" :type="pwd_type" placeholder="Secure Password" label="Password" density="compact" append-inner-icon="mdi-eye" @click:append-inner="pwd_type!=pwd_type"/>
            </v-card-text>
            <v-card-actions class="d-flex flex-column align-center" >
                <v-btn id="loginButton" @click="handleSignup" color="primary" block tonal>Sign Up</v-btn>
                <v-btn id="changeToSignup" @click="loadLogin" block outlined>Login Instead</v-btn>
            </v-card-actions>
        </v-container>
    </v-card>
</template>
  
<script>
import { useUserStore } from "@/stores/user";

export default {
    name: "SignupComponent",
    setup(){
        const userStore = useUserStore();
        return {userStore}
    },
    data() {
        return {
            _username: "",
            _password: "",
            error: null,
            message: null,
            pwd_type: false
        };
    },
    methods: {
        async handleSignup() {
            try {
                this.error = null;
                this.message = null;
                const response = await this.userStore.signup(this.username, this.password);
                this.message = response.message;
                this.$emit('signupSubmitted', {username: this._username, password: this._password});
                this.username = "";
                this.password = "";
            } catch (err) {
                this.error = err.message || "An error occurred during signup.";
            }
            
        },
        async handleLogout (){
            try {
                await this.userStore.logout();
                alert("Logged out!");
                this.$emit('loggedOut')
            } catch (error) {
                alert(error);   
            }
            
        },
        loadLogin(){
            this.$emit('changeToLogin', {username: this._username, password: this._password}); //we conveniently pass the username and password to the parent component, so that if the user decides to login, they don't have to retype the username and password
        }
    },
    emits: ['changeToLogin','signupSubmitted', 'loggedOut'],
    props: {
        username: {
            type: String,
            required: false
        },
        password: {
            type: String,
            required: false
        }
    },
    onload(){
        this._username = this.username;
        this._password = this.password;
    }
};
</script>

