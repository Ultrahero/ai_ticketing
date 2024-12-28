<template>
    <div class="explore-container" @mouseover="expandExplore" @mouseleave="collapseExplore">
        <div class="explore-bar" :class="{ expanded: isExpanded }">
            <v-icon :class="`fas fa-explore explore-icon ${isExpanded?'explore-button':''}`" @click.stop="handleExplore">mdi-compass-outline</v-icon>
            <div v-if="isExpanded" class="explore-input">
                <input type="text" id="exploreInput" placeholder="Explore..."></input>
                <v-icon class="fas fa-filter filter-icon">mdi-filter</v-icon>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            isExpanded: false,
            value: "",
        };
    },
    mounted(){
        //register the [ENTER] keypress whenever the search bar is non-emptied
        window.addEventListener('keyup', (e) => {
            if(e.key === 'Enter'){
                const explore_element = document.getElementById('exploreInput');
                if(explore_element!=null && explore_element.value.length > 0){
                    console.log("exploring for (setup): ", explore_element.value);
                    
                    // emit the search event
                    this.$emit('explore' , explore_element.value);
                    // clear the search bar
                    explore_element.value = "";
                }
            }
        });
    },
    methods: {
        handleExplore (){
            const explore_element = document.getElementById('exploreInput');
            if( explore_element.value.length > 0){
                console.log("exploring for (setup): ", explore_element.value);
                // emit the search event
                this.$emit('explore' , explore_element.value);
                console.log("explore event emitted");
                // clear the search bar
                explore_element.value = "";
            }
        },
        expandExplore() {
            this.isExpanded = true;
            this.$nextTick(() => {
                const explore_element= document.getElementById('exploreInput');
                explore_element.value = this.value;
            });
            this.$emit('expanded');
        },
        collapseExplore() {
            const explore_element = document.getElementById('exploreInput');
            this.value = explore_element.value;
            this.isExpanded = false;
            
        },
    },
    emits: ['explore', 'expanded'],
};
</script>

<style scoped>
.explore-container {
    display: flex;
    align-items: center;
}

.explore-bar {
    display: flex;
    align-items: center;
    transition: width 0.3s ease;
    border: none;
    width: 40px;
    overflow: hidden;
    padding: 5px;
}

.explore-bar.expanded {
    width: 200px;
    border: 1px solid #ccc;
    border-radius: 25px;
}

.explore-input {
    display: flex;
    align-content: space-between;
    flex-direction: row;
    flex-grow: 1;
}

.explore-icon,
.filter-icon {
    margin: 0 2px;
    transition: margin 0.3s ease;
}

.explore-icon.expanded,
.filter-icon.epanded {
    margin: 0 5px;
}

.explore-button {
    cursor: pointer;
    transition: transform 0.3s ease;
}

.explore-button:hover {
    transform: scale(1.1);
}

.explore-button:active {
    transform: scale(0.9);
}

input {
    border: none;
    outline: none;
    width: 100%;
}
</style>