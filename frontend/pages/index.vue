<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
await navigateTo('/hosts')
</script>
