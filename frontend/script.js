function selectRole(role) {
    localStorage.setItem("userRole", role);
    window.location.href = "/dashboard";
}