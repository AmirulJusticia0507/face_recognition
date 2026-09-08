<script setup>
import { ref, onMounted, computed } from 'vue'
import { settingsApi } from '../services/api'
import Swal from 'sweetalert2'

const activeTab = ref('users')

// Users State
const users = ref([])
const loadingUsers = ref(false)
const userSearch = ref('')
const currentPage = ref(1)
const totalUsers = ref(0)
const totalPages = ref(1)

// Roles State
const roles = ref([])
const loadingRoles = ref(false)

// Permissions State
const availablePermissions = ref([])
const loadingPermissions = ref(false)

// Modals
const showUserModal = ref(false)
const isEditingUser = ref(false)
const userForm = ref({
  id: null,
  username: '',
  password: '',
  email: '',
  first_name: '',
  last_name: '',
  is_staff: false,
  roles: []
})

const showRoleModal = ref(false)
const isEditingRole = ref(false)
const roleForm = ref({
  id: null,
  name: '',
  permissions: []
})

// Fetch Users
const fetchUsers = async () => {
  loadingUsers.value = true
  try {
    const res = await settingsApi.getUsers({
      search: userSearch.value,
      page: currentPage.value
    })
    users.value = res.data.results || res.data
    totalUsers.value = res.data.count || users.value.length
    totalPages.value = res.data.total_pages || Math.ceil(totalUsers.value / 20) || 1
  } catch (err) {
    console.error(err)
    Swal.fire('Error', 'Gagal memuat data pengguna.', 'error')
  } finally {
    loadingUsers.value = false
  }
}

// Fetch Roles
const fetchRoles = async () => {
  loadingRoles.value = true
  try {
    const res = await settingsApi.getRoles()
    roles.value = res.data
  } catch (err) {
    console.error(err)
    Swal.fire('Error', 'Gagal memuat data role.', 'error')
  } finally {
    loadingRoles.value = false
  }
}

// Fetch Permissions
const fetchPermissions = async () => {
  loadingPermissions.value = true
  try {
    const res = await settingsApi.getPermissions()
    availablePermissions.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loadingPermissions.value = false
  }
}

// User Actions
const openAddUserModal = () => {
  isEditingUser.value = false
  userForm.value = {
    id: null,
    username: '',
    password: '',
    email: '',
    first_name: '',
    last_name: '',
    is_staff: false,
    roles: []
  }
  showUserModal.value = true
}

const openEditUserModal = (user) => {
  isEditingUser.value = true
  userForm.value = {
    id: user.id,
    username: user.username,
    password: '',
    email: user.email || '',
    first_name: user.first_name || user.name.split(' ')[0] || '',
    last_name: user.last_name || user.name.split(' ').slice(1).join(' ') || '',
    is_staff: user.is_staff,
    roles: user.roles ? user.roles.map(r => r.id) : []
  }
  showUserModal.value = true
}

const saveUser = async () => {
  if (!userForm.value.username) {
    Swal.fire('Peringatan', 'Username wajib diisi.', 'warning')
    return
  }
  if (!isEditingUser.value && !userForm.value.password) {
    Swal.fire('Peringatan', 'Password wajib diisi untuk user baru.', 'warning')
    return
  }

  try {
    if (isEditingUser.value) {
      await settingsApi.updateUser(userForm.value.id, userForm.value)
      Swal.fire('Berhasil', 'Data pengguna berhasil diperbarui.', 'success')
    } else {
      await settingsApi.createUser(userForm.value)
      Swal.fire('Berhasil', 'User baru berhasil dibuat.', 'success')
    }
    showUserModal.value = false
    fetchUsers()
  } catch (err) {
    const msg = err.response?.data?.error || 'Gagal menyimpan user.'
    Swal.fire('Error', msg, 'error')
  }
}

const toggleUserActive = async (user) => {
  try {
    const res = await settingsApi.toggleUserActive(user.id)
    user.is_active = res.data.is_active
    Swal.fire('Berhasil', `Status user ${user.username} telah diperbarui.`, 'success')
  } catch (err) {
    const msg = err.response?.data?.error || 'Gagal mengubah status user.'
    Swal.fire('Error', msg, 'error')
  }
}

const deleteUser = async (user) => {
  const result = await Swal.fire({
    title: 'Hapus User?',
    text: `Apakah Anda yakin ingin menghapus user ${user.username}?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Ya, Hapus',
    cancelButtonText: 'Batal',
    confirmButtonColor: '#ef4444'
  })

  if (result.isConfirmed) {
    try {
      await settingsApi.deleteUser(user.id)
      Swal.fire('Berhasil', 'User berhasil dihapus.', 'success')
      fetchUsers()
    } catch (err) {
      const msg = err.response?.data?.error || 'Gagal menghapus user.'
      Swal.fire('Error', msg, 'error')
    }
  }
}

// Role Actions
const openAddRoleModal = () => {
  isEditingRole.value = false
  roleForm.value = { id: null, name: '', permissions: [] }
  showRoleModal.value = true
}

const openEditRoleModal = async (role) => {
  isEditingRole.value = true
  try {
    const res = await settingsApi.getRole(role.id)
    const detail = res.data
    roleForm.value = {
      id: detail.id,
      name: detail.name,
      permissions: detail.permissions ? detail.permissions.map(p => p.id) : []
    }
    showRoleModal.value = true
  } catch (err) {
    Swal.fire('Error', 'Gagal mengambil detail role.', 'error')
  }
}

const saveRole = async () => {
  if (!roleForm.value.name.trim()) {
    Swal.fire('Peringatan', 'Nama role wajib diisi.', 'warning')
    return
  }

  try {
    if (isEditingRole.value) {
      await settingsApi.updateRole(roleForm.value.id, roleForm.value)
      Swal.fire('Berhasil', 'Role berhasil diperbarui.', 'success')
    } else {
      await settingsApi.createRole(roleForm.value)
      Swal.fire('Berhasil', 'Role baru berhasil dibuat.', 'success')
    }
    showRoleModal.value = false
    fetchRoles()
  } catch (err) {
    const msg = err.response?.data?.error || 'Gagal menyimpan role.'
    Swal.fire('Error', msg, 'error')
  }
}

const deleteRole = async (role) => {
  const result = await Swal.fire({
    title: 'Hapus Role?',
    text: `Apakah Anda yakin ingin menghapus role "${role.name}"?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Ya, Hapus',
    cancelButtonText: 'Batal',
    confirmButtonColor: '#ef4444'
  })

  if (result.isConfirmed) {
    try {
      await settingsApi.deleteRole(role.id)
      Swal.fire('Berhasil', 'Role berhasil dihapus.', 'success')
      fetchRoles()
    } catch (err) {
      const msg = err.response?.data?.error || 'Gagal menghapus role.'
      Swal.fire('Error', msg, 'error')
    }
  }
}

const togglePermissionSelection = (permId) => {
  const idx = roleForm.value.permissions.indexOf(permId)
  if (idx > -1) {
    roleForm.value.permissions.splice(idx, 1)
  } else {
    roleForm.value.permissions.push(permId)
  }
}

const isGroupAllSelected = (groupPerms) => {
  return groupPerms.every(p => roleForm.value.permissions.includes(p.id))
}

const toggleGroupPermissions = (groupPerms) => {
  if (isGroupAllSelected(groupPerms)) {
    groupPerms.forEach(p => {
      const idx = roleForm.value.permissions.indexOf(p.id)
      if (idx > -1) roleForm.value.permissions.splice(idx, 1)
    })
  } else {
    groupPerms.forEach(p => {
      if (!roleForm.value.permissions.includes(p.id)) {
        roleForm.value.permissions.push(p.id)
      }
    })
  }
}

onMounted(() => {
  fetchUsers()
  fetchRoles()
  fetchPermissions()
})
</script>

<template>
  <div class="space-y-6 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Settings & Access Control</h1>
        <p class="text-gray-500 dark:text-gray-400 mt-1">Kelola Pengguna, Role, dan Hak Akses System (RBAC)</p>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="border-b border-gray-200 dark:border-dark-700">
      <nav class="-mb-px flex space-x-8" aria-label="Tabs">
        <button
          @click="activeTab = 'users'"
          :class="[
            activeTab === 'users'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400 font-semibold'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 transition-colors'
          ]"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          User Permissions ({{ users.length }})
        </button>

        <button
          @click="activeTab = 'roles'"
          :class="[
            activeTab === 'roles'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400 font-semibold'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 transition-colors'
          ]"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          Role Permissions ({{ roles.length }})
        </button>
      </nav>
    </div>

    <!-- TAB 1: USERS MANAGEMENT -->
    <div v-if="activeTab === 'users'" class="space-y-4">
      <!-- Search & Add User Toolbar -->
      <div class="flex flex-col sm:flex-row justify-between items-center gap-4 bg-white dark:bg-dark-800 p-4 rounded-xl shadow-sm border border-gray-200 dark:border-dark-700">
        <div class="relative w-full sm:w-80">
          <input
            v-model="userSearch"
            @keyup.enter="fetchUsers"
            type="text"
            placeholder="Cari user (nama, username, email)..."
            class="w-full pl-10 pr-4 py-2 border rounded-lg text-sm bg-gray-50 dark:bg-dark-900 border-gray-300 dark:border-dark-700 focus:ring-2 focus:ring-primary-500 focus:outline-none dark:text-white"
          />
          <svg class="w-5 h-5 text-gray-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        <button
          @click="openAddUserModal"
          class="w-full sm:w-auto px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2 transition-colors shadow"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Tambah User Baru
        </button>
      </div>

      <!-- Users Table -->
      <div class="bg-white dark:bg-dark-800 rounded-xl shadow-sm border border-gray-200 dark:border-dark-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm text-gray-600 dark:text-gray-300">
            <thead class="bg-gray-50 dark:bg-dark-900 text-gray-700 dark:text-gray-200 uppercase font-semibold text-xs border-b border-gray-200 dark:border-dark-700">
              <tr>
                <th class="px-6 py-4">User</th>
                <th class="px-6 py-4">Email</th>
                <th class="px-6 py-4">Role Assigned</th>
                <th class="px-6 py-4">Status</th>
                <th class="px-6 py-4 text-right">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-dark-700">
              <tr v-if="loadingUsers">
                <td colspan="5" class="px-6 py-8 text-center text-gray-500">Memuat data pengguna...</td>
              </tr>
              <tr v-else-if="users.length === 0">
                <td colspan="5" class="px-6 py-8 text-center text-gray-500">Tidak ada user ditemukan.</td>
              </tr>
              <tr v-else v-for="user in users" :key="user.id" class="hover:bg-gray-50 dark:hover:bg-dark-700/50 transition-colors">
                <td class="px-6 py-4">
                  <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-full bg-primary-100 text-primary-700 dark:bg-primary-900/50 dark:text-primary-300 font-bold flex items-center justify-center text-sm">
                      {{ user.username.charAt(0).toUpperCase() }}
                    </div>
                    <div>
                      <p class="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                        {{ user.name }}
                        <span v-if="user.is_superuser" class="px-2 py-0.5 text-[10px] font-semibold bg-purple-100 text-purple-700 dark:bg-purple-900/50 dark:text-purple-300 rounded">Superadmin</span>
                        <span v-else-if="user.is_staff" class="px-2 py-0.5 text-[10px] font-semibold bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300 rounded">Staff</span>
                      </p>
                      <p class="text-xs text-gray-500">@{{ user.username }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 text-gray-600 dark:text-gray-400">
                  {{ user.email || '-' }}
                </td>
                <td class="px-6 py-4">
                  <div class="flex flex-wrap gap-1">
                    <span v-if="!user.roles || user.roles.length === 0" class="text-xs text-gray-400 italic">Tanpa Role</span>
                    <span
                      v-for="r in user.roles"
                      :key="r.id"
                      class="px-2.5 py-1 text-xs rounded-full bg-indigo-50 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300 font-medium"
                    >
                      {{ r.name }}
                    </span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <button
                    @click="toggleUserActive(user)"
                    :class="[
                      user.is_active
                        ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300'
                        : 'bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300',
                      'px-3 py-1 rounded-full text-xs font-semibold inline-flex items-center gap-1.5 transition-all hover:opacity-80'
                    ]"
                  >
                    <span class="w-2 h-2 rounded-full" :class="user.is_active ? 'bg-emerald-500' : 'bg-rose-500'"></span>
                    {{ user.is_active ? 'Aktif' : 'Nonaktif' }}
                  </button>
                </td>
                <td class="px-6 py-4 text-right">
                  <div class="flex items-center justify-end gap-2">
                    <button
                      @click="openEditUserModal(user)"
                      class="p-1.5 text-gray-500 hover:text-primary-600 hover:bg-gray-100 dark:hover:bg-dark-700 rounded-lg transition-colors"
                      title="Edit User"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      @click="deleteUser(user)"
                      class="p-1.5 text-gray-500 hover:text-rose-600 hover:bg-gray-100 dark:hover:bg-dark-700 rounded-lg transition-colors"
                      title="Hapus User"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination Users -->
        <div v-if="totalPages > 1" class="px-4 py-3 border-t border-gray-100 dark:border-dark-700 flex items-center justify-between">
          <div class="text-sm text-gray-500">
            Halaman {{ currentPage }} dari {{ totalPages }} ({{ totalUsers }} user)
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="currentPage--; fetchUsers()"
              :disabled="currentPage === 1"
              class="px-3 py-1.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Sebelumnya
            </button>
            <button
              @click="currentPage++; fetchUsers()"
              :disabled="currentPage === totalPages"
              class="px-3 py-1.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Berikutnya
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: ROLES MANAGEMENT -->
    <div v-if="activeTab === 'roles'" class="space-y-4">
      <div class="flex flex-col sm:flex-row justify-between items-center gap-4 bg-white dark:bg-dark-800 p-4 rounded-xl shadow-sm border border-gray-200 dark:border-dark-700">
        <div>
          <h3 class="font-semibold text-gray-900 dark:text-white">Daftar Role Hak Akses</h3>
          <p class="text-xs text-gray-500">Kelola grup role dan permissions per modul untuk sistem security.</p>
        </div>
        <button
          @click="openAddRoleModal"
          class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-medium flex items-center gap-2 transition-colors shadow"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Buat Role Baru
        </button>
      </div>

      <!-- Roles Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-if="loadingRoles" class="col-span-full py-8 text-center text-gray-500">
          Memuat daftar role...
        </div>
        <div
          v-else
          v-for="role in roles"
          :key="role.id"
          class="bg-white dark:bg-dark-800 rounded-xl p-5 border border-gray-200 dark:border-dark-700 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
        >
          <div>
            <div class="flex items-center justify-between mb-3">
              <span class="px-3 py-1 bg-primary-100 text-primary-800 dark:bg-primary-900/50 dark:text-primary-300 font-bold rounded-lg text-sm">
                {{ role.name }}
              </span>
              <span class="text-xs font-medium text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-dark-700 px-2.5 py-1 rounded-full">
                {{ role.user_count }} Pengguna
              </span>
            </div>

            <div class="mt-4">
              <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Permissions Granted ({{ role.permissions ? role.permissions.length : 0 }})</p>
              <div class="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto pr-1">
                <span
                  v-for="p in role.permissions"
                  :key="p.id"
                  class="text-[11px] px-2 py-0.5 bg-gray-100 dark:bg-dark-700 text-gray-700 dark:text-gray-300 rounded font-mono"
                >
                  {{ p.codename }}
                </span>
                <span v-if="!role.permissions || role.permissions.length === 0" class="text-xs text-gray-400 italic">Belum ada permission.</span>
              </div>
            </div>
          </div>

          <div class="mt-6 pt-4 border-t border-gray-100 dark:border-dark-700 flex justify-end gap-2">
            <button
              @click="openEditRoleModal(role)"
              class="px-3 py-1.5 text-xs font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-dark-700 hover:bg-gray-200 dark:hover:bg-dark-600 rounded-lg transition-colors flex items-center gap-1.5"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Edit Permissions
            </button>
            <button
              @click="deleteRole(role)"
              class="px-3 py-1.5 text-xs font-medium text-rose-600 bg-rose-50 hover:bg-rose-100 dark:bg-rose-900/30 dark:hover:bg-rose-900/50 rounded-lg transition-colors flex items-center gap-1.5"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL ADD/EDIT USER -->
    <div v-if="showUserModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div class="bg-white dark:bg-dark-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-gray-200 dark:border-dark-700 space-y-4">
        <div class="flex justify-between items-center pb-3 border-b border-gray-100 dark:border-dark-700">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">
            {{ isEditingUser ? 'Edit User' : 'Tambah User Baru' }}
          </h3>
          <button @click="showUserModal = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="space-y-4 max-h-[70vh] overflow-y-auto pr-1">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">First Name</label>
              <input v-model="userForm.first_name" type="text" class="w-full px-3 py-2 text-sm border rounded-lg bg-gray-50 dark:bg-dark-900 border-gray-300 dark:border-dark-700 dark:text-white" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">Last Name</label>
              <input v-model="userForm.last_name" type="text" class="w-full px-3 py-2 text-sm border rounded-lg bg-gray-50 dark:bg-dark-900 border-gray-300 dark:border-dark-700 dark:text-white" />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">Username *</label>
            <input v-model="userForm.username" type="text" :disabled="isEditingUser" class="w-full px-3 py-2 text-sm border rounded-lg bg-gray-50 dark:bg-dark-900 border-gray-300 dark:border-dark-700 dark:text-white disabled:opacity-60" />
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">Email</label>
            <input v-model="userForm.email" type="email" class="w-full px-3 py-2 text-sm border rounded-lg bg-gray-50 dark:bg-dark-900 border-gray-300 dark:border-dark-700 dark:text-white" />
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Password {{ isEditingUser ? '(Kosongkan jika tidak ingin diubah)' : '*' }}
            </label>
            <input v-model="userForm.password" type="password" class="w-full px-3 py-2 text-sm border rounded-lg bg-gray-50 dark:bg-dark-900 border-gray-300 dark:border-dark-700 dark:text-white" />
          </div>

          <!-- Select Roles -->
          <div>
            <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">Pilih Role</label>
            <div class="space-y-2 border border-gray-200 dark:border-dark-700 p-3 rounded-lg bg-gray-50 dark:bg-dark-900">
              <div v-for="r in roles" :key="r.id" class="flex items-center gap-2">
                <input
                  type="checkbox"
                  :id="`role-user-${r.id}`"
                  :value="r.id"
                  v-model="userForm.roles"
                  class="rounded text-primary-600 focus:ring-primary-500"
                />
                <label :for="`role-user-${r.id}`" class="text-sm text-gray-800 dark:text-gray-200 cursor-pointer font-medium">
                  {{ r.name }}
                </label>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2 pt-2">
            <input type="checkbox" id="is_staff" v-model="userForm.is_staff" class="rounded text-primary-600 focus:ring-primary-500" />
            <label for="is_staff" class="text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer">Akses Staff / Dashboard Admin</label>
          </div>
        </div>

        <div class="flex justify-end gap-3 pt-4 border-t border-gray-100 dark:border-dark-700">
          <button @click="showUserModal = false" class="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-dark-700 rounded-lg">Batal</button>
          <button @click="saveUser" class="px-4 py-2 text-sm bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium shadow">Simpan</button>
        </div>
      </div>
    </div>

    <!-- MODAL ADD/EDIT ROLE & PERMISSIONS -->
    <div v-if="showRoleModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div class="bg-white dark:bg-dark-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-gray-200 dark:border-dark-700 space-y-4">
        <div class="flex justify-between items-center pb-3 border-b border-gray-100 dark:border-dark-700">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">
            {{ isEditingRole ? 'Edit Role Permissions' : 'Buat Role Baru' }}
          </h3>
          <button @click="showRoleModal = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="space-y-4 max-h-[70vh] overflow-y-auto pr-1">
          <div>
            <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">Nama Role *</label>
            <input v-model="roleForm.name" type="text" placeholder="Contoh: Manager, Analyst, Verifier" class="w-full px-3 py-2 text-sm border rounded-lg bg-gray-50 dark:bg-dark-900 border-gray-300 dark:border-dark-700 dark:text-white" />
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">Pilih System Permissions</label>

            <div class="space-y-4">
              <div
                v-for="group in availablePermissions"
                :key="group.model"
                class="border border-gray-200 dark:border-dark-700 rounded-xl p-4 bg-gray-50/50 dark:bg-dark-900/50"
              >
                <div class="flex items-center justify-between mb-3 border-b border-gray-200 dark:border-dark-700 pb-2">
                  <span class="font-bold text-xs uppercase tracking-wider text-primary-700 dark:text-primary-400">
                    Modul: {{ group.model }}
                  </span>
                  <button
                    @click="toggleGroupPermissions(group.permissions)"
                    type="button"
                    class="text-xs text-primary-600 dark:text-primary-400 hover:underline font-medium"
                  >
                    {{ isGroupAllSelected(group.permissions) ? 'Pilih Semua (Clear)' : 'Pilih Semua' }}
                  </button>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <div
                    v-for="perm in group.permissions"
                    :key="perm.id"
                    @click="togglePermissionSelection(perm.id)"
                    :class="[
                      roleForm.permissions.includes(perm.id)
                        ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/30 text-primary-900 dark:text-primary-200'
                        : 'border-gray-200 dark:border-dark-700 bg-white dark:bg-dark-800 text-gray-700 dark:text-gray-300',
                      'p-2.5 rounded-lg border text-xs font-medium cursor-pointer flex items-center gap-2 transition-all'
                    ]"
                  >
                    <input
                      type="checkbox"
                      :checked="roleForm.permissions.includes(perm.id)"
                      class="rounded text-primary-600 focus:ring-primary-500"
                      @click.stop
                      @change="togglePermissionSelection(perm.id)"
                    />
                    <div class="truncate">
                      <p class="font-semibold">{{ perm.name }}</p>
                      <p class="text-[10px] text-gray-400 font-mono">{{ perm.codename }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-3 pt-4 border-t border-gray-100 dark:border-dark-700">
          <button @click="showRoleModal = false" class="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-dark-700 rounded-lg">Batal</button>
          <button @click="saveRole" class="px-4 py-2 text-sm bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium shadow">Simpan Role</button>
        </div>
      </div>
    </div>
  </div>
</template>