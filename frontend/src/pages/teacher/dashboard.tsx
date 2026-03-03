'use client'

import React from 'react'
import TeacherDashboard from '@/components/Teacher/TeacherDashboard'

export default function TeacherDashboardPage() {
  // TODO: Get teacher ID from auth context
  const teacherId = 1

  return <TeacherDashboard teacherId={teacherId} />
}
