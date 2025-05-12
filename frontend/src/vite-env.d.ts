// vite-env.d.ts
/// <reference types="vite-plugin-pages/client-react" />
/// <reference types="vite/client" />

// 扩展React的InputHTMLAttributes接口，增加directory和webkitdirectory属性
declare module 'react' {
  interface InputHTMLAttributes<T> extends HTMLAttributes<T> {
    directory?: string;
    webkitdirectory?: string;
  }
}
