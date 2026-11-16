// Sample data only. Replace by connecting the backend (see services/api.js)
export const ITEMS = [
 {id:'UT-8821',type:'found',title:'Space Gray MacBook Air M2 13"',description:'Covered with NASA mission logo and Python syntax stickers. Left plugged into wall outlet near reading desks.',category:'Electronics',location:'Chemistry Library, 3rd Floor',time:'45 mins ago'},
 {id:'UT-8819',type:'found',title:'Matte Black Hydro Flask 24oz',description:'Silver dent on bottom rim. Black flex straw cap with slight scuffs on rubber handle.',category:'Bottles & Gear',location:'Gregory Gym, Locker Bay 4',time:'2 hrs ago'},
 {id:'UT-8804',type:'found',title:'Brown Leather Bellroy Slim Wallet',description:'Contains a student ID and driver license. Found near the food court booths.',category:'IDs & Keys',location:'Union Food Court',time:'Yesterday'},
 {id:'UT-8792',type:'found',title:'Sony WH-1000XM5 Headphones Silver',description:'Pristine condition in original zipped carrying case with aux cord.',category:'Electronics',location:'Hackerman Building, Hall 1.104',time:'Yesterday'},
 {id:'UT-8780',type:'found',title:'Set of 3 Dorm Keys & Longhorn Lanyard',description:'Three silver and brass keys with blue plastic topper, university dorm fob, burnt orange fabric lanyard.',category:'IDs & Keys',location:'Speedway Info Booth',time:'3 hrs ago'},
 {id:'UT-8755',type:'found',title:'Patagonia Better Sweater Navy M',description:'Mens medium quarter-zip fleece pullover left on study chair. AirPods charging wire in chest pocket.',category:'Apparel',location:'Undergraduate Library, 2nd Floor',time:'5 hrs ago'},
 {id:'UT-8761',type:'lost',title:'TI-84 Plus CE Graphing Calculator',description:'Mint green pastel case, slide cover with cursive name initials S.M. scratched into interior.',category:'Electronics',location:'Welch Hall, Organic Chem Auditorium',time:'2 days ago'},
 {id:'UT-8742',type:'lost',title:'Ray-Ban Wayfarer Classic Sunglasses',description:'Gloss black frames with polarized G-15 green lenses. Lost while sitting on lawn near fountain.',category:'Accessories',location:'South Mall Lawn',time:'Yesterday'},
 {id:'UT-8830',type:'lost',title:'Matte Black Hydro Flask with silver dent',description:'Black Hydro Flask 24oz, silver dent on bottom rim, black straw cap.',category:'Bottles & Gear',location:'Rec Sports Center',time:'3 hrs ago'},
 {id:'UT-8831',type:'lost',title:'Brown leather wallet with student ID',description:'Slim brown leather wallet, student ID inside. Lost around the food court.',category:'IDs & Keys',location:'Union Food Court',time:'Yesterday'},
 {id:'UT-8832',type:'lost',title:'AirPods Pro in orange silicone case',description:'AirPods Pro 2nd Gen, orange silicone case with silver clip.',category:'Electronics',location:'Student Activity Center',time:'4 hrs ago'},
 {id:'UT-8812',type:'found',title:'AirPods Pro (2nd Gen) orange silicone case',description:'Housed in an orange silicone case with silver clip. Bluetooth broadcast ID visible.',category:'Electronics',location:'Student Activity Center',time:'4 hrs ago'},
]
export const NOTIFICATIONS = [
 {id:1,title:'Possible match for your Hydro Flask report',body:'A found-item listing is similar. Review it and verify ownership.',time:'10 mins ago',read:false,to:'/matches'},
 {id:2,title:'Claim received on UT-8812',body:'The desk will review your verification answer.',time:'1 hr ago',read:false,to:'/verify/UT-8812'},
 {id:3,title:'Report submitted',body:'Your lost wallet report is now visible in the directory.',time:'Yesterday',read:true,to:'/explore'},
]
