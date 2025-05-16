import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import RecordsPage from '../views/RecordsPage.vue'
import GetMoney from '@/views/GetMoney.vue'
import Pensia from '@/views/Pensia.vue'
import Shop from '@/views/Shop.vue'
import Register from '@/components/Register.vue'
import Profile from '@/views/Profile.vue'
import ProductNft1 from '@/views/Products/ProductNft1.vue'
import ProductNft2 from '@/views/Products/ProductNft2.vue'
import ProductNft3 from '@/views/Products/ProductNft3.vue'
import ProductNft4 from '@/views/Products/ProductNft4.vue'
import ProductNft5 from '@/views/Products/ProductNft5.vue'
import MyNft from '@/views/MyNft.vue'
import CasinoPage from '@/views/CasinoPage.vue'
import TonConnectTopup from '@/views/ton-connect-topup.vue'



const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [  
    {
      path: '/mynft',
      name: 'MY-NFT',
      component: MyNft,
    },
    {
      path: '/product/1',
      name: 'NFT1',
      component: ProductNft1,
    },
    {
      path: '/product/2',
      name: 'NFT2',
      component: ProductNft2,
    },
    {
      path: '/product/3',
      name: 'NFT3',
      component: ProductNft3,
    },
    {
      path: '/product/4',
      name: 'NFT4',
      component: ProductNft4,
    },
    {
      path: '/product/5',
      name: 'NFT5',
      component: ProductNft5,
    },
    {
      path: '/ton-connect-topup',
      name: 'ton-connect-topup',
      component: TonConnectTopup,
    },
    {
      path: '/profile',
      name: 'Profile',
      component: Profile,
      props: true // This allows passing route params as props
    },
    {
      path: '/register',
      name: 'Register',
      component: Register,
    },
    {
      path: '/casinopage',
      name: 'CasinoPage',
      component: CasinoPage,
    },
    {
      path: '/shop',
      name: 'Shop',
      component: Shop,
    },
    {
      path: '/pensia',
      name: 'Pensia',
      component: Pensia,
    },
    {
      path: '/getmoney',
      name: 'GetMoney',
      component: GetMoney,
    },
    {
      path: '/records',
      name: 'RecordsPage',
      component: RecordsPage,
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/tasks',
      name: 'tasks',
      component: () => import('../views/TasksView.vue'),
    },
    {
      path: '/friends',
      name: 'friends',
      component: () => import('../views/FriendsView.vue'),
    },
  ],
})

export default router
