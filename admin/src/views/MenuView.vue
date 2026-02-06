<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">🍽️ 菜单管理</h1>
      <el-button type="primary" @click="showAddDialog" :icon="Plus">添加菜品</el-button>
    </div>

    <el-table :data="menuItems" v-loading="loading" stripe style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="菜品名称" width="150" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="price" label="价格" width="100">
        <template #default="{ row }">
          <span style="color: #f56c6c; font-weight: bold">¥{{ row.price.toFixed(2) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="stock" label="库存" width="100" />
      <el-table-column prop="is_available" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_available ? 'success' : 'info'">
            {{ row.is_available ? '上架' : '下架' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="editItem(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteItem(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑菜品' : '添加菜品'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="菜品名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入菜品名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入菜品描述" />
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="form.price" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="form.stock" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态" prop="is_available">
          <el-switch v-model="form.is_available" active-text="上架" inactive-text="下架" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getMenu, createMenuItem, updateMenuItem, deleteMenuItem } from '../api/restaurant'

const loading = ref(false)
const menuItems = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const submitting = ref(false)

const form = reactive({
  id: null,
  name: '',
  description: '',
  price: 0,
  stock: 0,
  is_available: true
})

const rules = {
  name: [{ required: true, message: '请输入菜品名称', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  stock: [{ required: true, message: '请输入库存', trigger: 'blur' }]
}

const loadMenu = async () => {
  loading.value = true
  try {
    menuItems.value = await getMenu(1)
  } catch (error) {
    ElMessage.error('加载菜单失败')
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const editItem = (item) => {
  isEdit.value = true
  Object.assign(form, item)
  dialogVisible.value = true
}

const deleteItem = async (item) => {
  try {
    await ElMessageBox.confirm(`确认删除菜品 ${item.name}?`, '确认删除', {
      type: 'warning'
    })

    await deleteMenuItem(item.id)
    ElMessage.success('删除成功')
    loadMenu()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    const data = {
      store_id: 1,
      name: form.name,
      description: form.description,
      price: form.price,
      stock: form.stock,
      is_available: form.is_available
    }

    if (isEdit.value) {
      await updateMenuItem(form.id, data)
      ElMessage.success('更新成功')
    } else {
      await createMenuItem(data)
      ElMessage.success('添加成功')
    }

    dialogVisible.value = false
    loadMenu()
  } catch (error) {
    if (error.message) {
      ElMessage.error('操作失败')
    }
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  formRef.value?.resetFields()
  Object.assign(form, {
    id: null,
    name: '',
    description: '',
    price: 0,
    stock: 0,
    is_available: true
  })
}

onMounted(() => {
  loadMenu()
})
</script>
