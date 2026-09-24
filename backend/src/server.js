import express from 'express'
import cors from 'cors'
import dotenv from 'dotenv'

dotenv.config()
const app = express()
const PORT = process.env.PORT || 5000

 app.use(cors())

app.get('/dashboard',(req,res)=>{
    console.log("Dashboard is accessed")
})

async function startServer() {
    try {
        await app.listen(PORT,()=>{
            console.log(`the server is running at ${PORT}`)
        })
    } catch (error) {
        console.error("server error",error)
    }
}
startServer()


