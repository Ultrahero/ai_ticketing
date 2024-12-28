<template>
    <div class="search-container" @mouseover="expandSearch" @mouseleave="collapseSearch">
        <div class="search-bar" :class="{ expanded: isExpanded }">
            <v-icon :class="`fas fa-search search-icon ${isExpanded?'search-button':''}`" @click.stop="handleSearch">mdi-magnify</v-icon>
            <div v-if="isExpanded" class="search-input">
                <input type="text" id="searchInput" placeholder="Search..."></input>
                <v-icon class="fas fa-filter filter-icon">mdi-filter</v-icon>
            </div>
            
        </div>
    </div>
</template>

<script>
export default {
    mounted(){
        window.addEventListener('keypress', (e) => {
            if(e.key === 'Enter'){
                const search_element = document.getElementById('searchInput');
                if(search_element!=null && search_element.value.length > 0){
                    console.log("searching for (setup): ", search_element.value);
                    // clear the search bar
                    this.$emit('search' , search_element.value);

                    search_element.value = "";
                    // emit the search event
                }
            }
        });
    },
    data() {
        return {
            isExpanded: false,
            value: "",
            q: "",
        };
    },
    methods: {
        handleSearch(){
            const search_element = document.getElementById('searchInput');
            if(search_element.value.length > 0){
                let val = search_element.value
                console.log("searching for (setup): ", val);
                // emit the search event
                this.$emit('search' , "onstant test");
                console.log("search event emitted", val);
                // clear the search bar
                search_element.value = "";
            }
        },
        expandSearch() {
            this.isExpanded = true;
            this.$nextTick(() => {
                const search_element = document.getElementById('searchInput');
                search_element.value = this.value;
            });
            this.$emit('expanded');
        },
        collapseSearch() {
            const search_element = document.getElementById('searchInput');
            this.value = search_element.value;
            this.isExpanded = false;
        },
    },
    emits: ['search', 'expanded'],
};
</script>

<style scoped>
.search-container {
    display: flex;
    align-items: center;
}

.search-bar {
    display: flex;
    align-items: center;
    transition: width 0.3s ease;
    border: none;
    width: 40px;
    overflow: hidden;
    padding: 5px;
}

.search-bar.expanded {
    width: 200px;
    border: 1px solid #ccc;
    border-radius: 25px;
}

.search-input {
    display: flex;
    align-content: space-between;
    flex-direction: row;
    flex-grow: 1;
}

.search-icon,
.filter-icon {
    margin: 0 2px;
    transition: margin 0.3s ease;
}

.search-icon.expanded,
.filter-icon.epanded {
    margin: 0 5px;
}

.search-button{
    cursor: pointer;
    transition: transform 0.3s ease;
}

.search-button:hover {
    transform: scale(1.1);
}

.search-button:active {
    transform: scale(0.9);
}

input {
    border: none;
    outline: none;
    width: 100%;
}
</style>