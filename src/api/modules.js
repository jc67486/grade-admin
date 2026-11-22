import request from './request'

export const login = (data) => request.post('/login', data)
export const getMe = () => request.get('/me')

export const getStudents = (params) => request.get('/students', { params })
export const createStudent = (data) => request.post('/students', data)
export const updateStudent = (id, data) => request.put(`/students/${id}`, data)
export const removeStudent = (id) => request.delete(`/students/${id}`)

export const getCourses = () => request.get('/courses')
export const getGrades = (params) => request.get('/grades', { params })
export const createGrade = (data) => request.post('/grades', data)
export const getStats = () => request.get('/stats')
