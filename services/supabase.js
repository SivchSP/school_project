
import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = 'https://jgkfvqiophgvswqvatbx.supabase.co'
const SUPABASE_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impna2Z2cWlvcGhndnN3cXZhdGJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk4ODI5NTMsImV4cCI6MjA1NTQ1ODk1M30.GTN1V9NJwnmwy8GmXOOz3SxepV7n4yVKkhLYZTYuFEQ'

const supabase = createClient(SUPABASE_URL, SUPABASE_API_KEY)

export default supabase

