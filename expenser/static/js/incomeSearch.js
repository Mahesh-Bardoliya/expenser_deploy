const searchField = document.querySelector("#searchField");
const tableOutput = document.querySelector(".table-output");
const appTable = document.querySelector(".app-table");
const tableBody = document.querySelector(".table-body");
tableOutput.style.display="none";
searchField.addEventListener("keyup", (e) => {
    const searchValue = e.target.value; 
    if (searchValue.trim().length > 0   ){
        console.log("searchValue", searchValue);
        tableBody.innerHTML="";
        fetch("/income/search-income",{
            body: JSON.stringify({searchText:searchValue}),
            method:"POST",
        })
        .then((res)=>res.json())
        .then((data)=>{
            console.log("data", data);
            appTable.style.display="none";
            tableOutput.style.display="block";            
                data.forEach((item) => {
                    tableBody.innerHTML+=`
                        <tr>
                            <td>${item.amount}</td>
                            <td>${item.source}</td>
                            <td>${item.description}</td>
                            <td>${item.date}</td>
                            <td><h3><a href="/income/edit-income/${item.id}"><i class="mdi mdi-pencil-box text-primary "></i></a><a href="/income/income-delete/${item.id}"><i class="mdi mdi-delete-forever text-danger "></i></a></h3></label></td>
                        </tr>`;
                });
            
        });
    }
    else{
        tableOutput.style.display="none";
        appTable.style.display="block";
        
    }
});