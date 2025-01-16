// check
function checkStats(){
move_analysis(move)
if(move_analysis(move) == "check"){
    if(move.turn =="white"){
    whiteCheck += 1
    if(discoveredCheck()){
        whiteDiscoveredCheck += 1
    }
    if(doubleCheck()){
        whiteDoubleCheck += 1
    }
    if(turn =="black"){
        blackCheck += 1
        if(discoveredCheck(move)){
            blackDiscoveredCheck += 1
        }
        if(doubleCheck()){
          blackDoubleCheck += 1
        }
    }
}
}
}

// zwischenzug

function checkZwichenzug(move){
    if(move.turn == "white"){
        if(move.isThreat() || move.isCheck() || move.isCapture() && move.isCapture()){
            
        }
    }

}


function checkMoveIsThreat(move){

    if(materialThreat(move) | 
){
}

function materialThreat(move){

}

function matingThreat(move){

}


function positionalThreat(move)