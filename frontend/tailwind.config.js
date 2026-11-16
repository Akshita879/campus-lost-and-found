// Tokens ported from the Stitch export (DESIGN.md + tailwind-config in code.html)
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: { extend: {
    colors: { primary:'#00685f','primary-container':'#008378','primary-fixed':'#89f5e7','on-primary':'#ffffff',
      background:'#f8f9ff','surface-lowest':'#ffffff','surface-low':'#eff4ff',surface:'#e5eeff','surface-high':'#dce9ff',
      'on-surface':'#0b1c30','on-surface-variant':'#3d4947',outline:'#6d7a77','outline-variant':'#bcc9c6',
      'secondary-container':'#dae2fd','on-secondary-container':'#5c647a',error:'#ba1a1a','error-container':'#ffdad6' },
    borderRadius: { DEFAULT:'0.25rem', lg:'0.5rem', xl:'0.75rem', '2xl':'1rem', full:'9999px' },
    fontFamily: { sans: ['"Plus Jakarta Sans Variable"','sans-serif'] },
    boxShadow: { card:'0 1px 3px 0 rgba(15,23,42,.04),0 1px 2px -1px rgba(15,23,42,.02)', lift:'0 10px 15px -3px rgba(15,23,42,.05),0 4px 6px -4px rgba(15,23,42,.03)' } } },
}
