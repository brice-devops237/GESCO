<template>
  <div class="h-100 d-flex align-center justify-md-space-between justify-center">
    <!-- 👉 Footer: left content -->
    <span class="d-flex align-center">
    Copyright
      &copy;
      {{ new Date().getFullYear() }}
    </span>
    <!-- 👉 Footer: right content -->
    <span class="d-md-flex gap-x-4 text-primary d-none">
      <a
        href="#"
        target="noopener noreferrer"
      >License</a>
      <a
        href="#"
        target="noopener noreferrer"
      >Support</a>
    </span>
  </div>
</template>
