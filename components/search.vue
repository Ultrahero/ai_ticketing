<template>
    <div class="search-container" @mouseover="expandSearch" @mouseleave="collapseSearch">
        <div class="search-bar" :class="{ expanded: isExpanded }">
            <v-icon class="fas fa-search search-icon">mdi-magnify</v-icon>
            <div v-if="isExpanded" class="search-input">
                <input type="text" id="searchInput" placeholder="Search..."></input>
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
        };
    },
    methods: {
        expandSearch() {
            this.isExpanded = true;
        },
        collapseSearch() {
            this.isExpanded = false;
        },
    },
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

input {
    border: none;
    outline: none;
    width: 100%;
}
</style>