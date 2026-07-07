export type Role = 'owner' | 'cashier'
export type OrderType = 'dine_in' | 'takeaway'
export type PaymentMethod = 'cash' | 'qris' | 'transfer'
export type OrderStatus = 'open' | 'paid' | 'void'

export interface Me {
  id: string
  tenant_id: string
  email: string
  full_name: string
  role: Role
  outlet_name?: string
}

export interface Category {
  id: string
  name: string
  sort_order: number
}

export interface MenuItem {
  id: string
  category_id?: string
  category_name?: string
  name: string
  price: number
  is_available: boolean
}

export interface OrderItem {
  id: string
  menu_item_id?: string
  name: string
  price: number
  quantity: number
  line_total: number
  note?: string
}

export interface Order {
  id: string
  order_number?: string
  order_type: OrderType
  table_no?: string
  status: OrderStatus
  subtotal: number
  total: number
  payment_method?: PaymentMethod
  paid_amount: number
  change_amount: number
  cashier_name?: string
  notes?: string
  items: OrderItem[]
  created_at: string
}

export interface CartLine {
  menu_item_id?: string
  name: string
  price: number
  quantity: number
}
