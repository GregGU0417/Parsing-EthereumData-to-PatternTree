import networkx as nx
import networkx.algorithms.isomorphism as iso
import pandas as pd
class PatternTreeParsing:
    def __init__(self, frame_list, platformToken,pattern_list):
        
        self.pattern_list=pattern_list
        self.frame_list = frame_list
        self.platformToken = platformToken
        self.list_of_parsing, self.graph=self.treestructure(frame_list, platformToken)
        self.simplify_tree = self.generate_new_tree(self.list_of_parsing, self.graph, 0, {})
        self.pattern_tree = self.pattern_parsing(frame_list, platformToken, self.pattern_list)
        self.discriptive_pattern_tree  =   self.discriptive_pattern_tree_generation(self.pattern_list,self.list_of_parsing,self.simplify_tree)
    def log4parsing(self,fromvalue, inputvalue):
       
        if inputvalue == '':
            return {"type": "empty"}
        elif inputvalue[0:64] != 'ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef':
            return {"type": "empty"}
        else:
            if (len(inputvalue)) < 101:
                return {"type": "empty"}
            tokenaddress = fromvalue
            segs = inputvalue.split(" ")
            if (len(segs) != 4):
                return {"type": "empty"}
            prezero1 = 40 - len(segs[1])
            prezero2 = 40 - len(segs[2])
            fromAddress = "0x" + "0" * prezero1 + segs[1]
            toAddress = "0x" + "0" * prezero2 + segs[2]
            nftTokenId = "0x" + segs[3]
            tokenId = eval(nftTokenId)
            typevalue = "transfer"
            zeroaddress = "0x" + "0" * 40
            if (fromAddress == zeroaddress and toAddress == zeroaddress):
                return {"type": "empty"}
            elif (fromAddress == zeroaddress):
                typevalue = "mint"
            elif (toAddress == zeroaddress ):
                typevalue = "burn"

            return {"type": typevalue, "from": fromAddress, "to": toAddress, "token": tokenaddress, "amount": 1,
                    "tokenID": tokenId}


    def log3parsing(self,fromvalue, amount, inputvalue):
        
        if inputvalue == '':
            return {"type": "empty"}
        elif inputvalue[0:64] != 'ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef':
            return {"type": "empty"}
        else:
            if amount == "":
                return {"type": "empty"}
            transfer_amount = eval("0x" + amount)
            tokenaddress = fromvalue
            segs = inputvalue.split(" ")
            if (len(segs) != 3):
                return {"type": "empty"}
            prezero1 = 40 - len(segs[1])
            prezero2 = 40 - len(segs[2])
            fromAddress = "0x" + "0" * prezero1 + segs[1]
            toAddress = "0x" + "0" * prezero2 + segs[2]
            typevalue = "transfer"
            zeroaddress = "0x" + "0" * 40
            if (fromAddress == zeroaddress and toAddress == zeroaddress):
                return {"type": "empty"}
            elif (fromAddress == zeroaddress):
                typevalue = "mint"
            elif (toAddress == zeroaddress):
                typevalue = "burn"

            return {"type": typevalue, "from": fromAddress, "to": toAddress, "token": tokenaddress,
                    "amount": transfer_amount, "tokenID": "empty"}
    def parseinternal(self,fromAddress,toAddress,token,amount):
        
        typevalue="transfer"
        zeroaddress="0x"+"0"*40
        if(fromAddress==zeroaddress and toAddress==zeroaddress):
            return {"type":"empty"}
        elif (fromAddress==zeroaddress):
            typrvalue="mint"
        elif (toAddress==zeroaddress):
            typevalue="burn"
        return {"type":typevalue,"from":fromAddress,"to":toAddress,"token":token,"amount":eval(amount),"tokenID":"empty"}
    

    def parsing(self,frame, platformToken):
        
        type_value = frame["type"]
        if (type_value == ''):
            return {"type": "empty"}
        elif (type_value == "LOG3"):
            return self.log3parsing(frame["from"], frame["value"], frame["input"])
        elif (type_value == "LOG4"):
            return self.log4parsing(frame["from"], frame["input"])
        elif (type_value == "CALL"):
            if frame["value"] == "" or frame["value"] == "0x0":
                return {"type": "empty"}
            if (frame["from"] == platformToken or frame["to"] == platformToken):
                return {"type": "empty"}
            else:
                return self.parseinternal(frame["from"], frame["to"], platformToken, frame["value"])
        elif (type_value == "CREATE"):
            if frame["value"] == "" or frame["value"] == "0x0":
                return {"type": "empty"}
            if (frame["contractCreated"] != "" and frame["contractCreated"] != None):
                return self.internalTransferFromCallFrame(
                    frame["from"], frame["contractCreated"], platformToken, frame["input"])
            else:
                return self.internalTransferFromCallFrame(
                    frame["from"], frame["contractCreated"], platformToken, frame["input"])

        elif (type_value == "CREATE2"):
            if frame["value"] == "" or frame["value"] == "0x0":
                return {"type": "empty"}
            if (frame["contractCreated"] != "" and frame["contractCreated"] != None):
                return self.internalTransferFromCallFrame(
                    frame["from"], frame["contractCreated"], platformToken, frame["input"])
        else:
            return {"type": "empty"}


    def treestructure(self,frame_list, platformToken):
       
        list_of_parsing = []
        list_of_frameID_dict = {}
        list_of_childcount = []
        for i in range(len(frame_list)):
            list_of_parsing.append(self.parsing(frame_list[i], platformToken))
            list_of_frameID_dict[frame_list[i]["frameId"]] = i
            list_of_childcount.append(frame_list[i]["childrenCount"])
        graph = {}
        for i in range(len(frame_list)):
            if (list_of_childcount[i] > 0):
                list_of_children = []
                for j in range(0, list_of_childcount[i]):
                    list_of_children.append(list_of_frameID_dict[frame_list[i]["frameId"] + "_" + str(j)])
                graph[i] = set(list_of_children)
        return [list_of_parsing, graph]


    def get_content(self,list_of_parsing,tree,sub_tree_node):
        return_list=[]
        if sub_tree_node not in list(tree.keys()):
            if list_of_parsing[sub_tree_node]['type']!="empty":
                return_list.append(list_of_parsing[sub_tree_node])
            return return_list
        else:
            if list_of_parsing[sub_tree_node]['type']!="empty":
                return_list.append(list_of_parsing[sub_tree_node])
            for node in tree[sub_tree_node]:
                return_list +=self.get_content(list_of_parsing,tree,node)
            return return_list

    def generate_new_tree(self,list_of_parsing,tree,root_node,return_tree):
        list_of_child_node=[]
        if root_node not in list(tree.keys()):
            return return_tree
        else:
            for child_node in tree[root_node]:
                if self.get_content(list_of_parsing,tree,child_node)!=[]:
                    list_of_child_node.append(child_node)
                    new_sub_tree=self.generate_new_tree(list_of_parsing,tree,child_node,return_tree)
                    return_tree = dict(list(return_tree.items()) + list(new_sub_tree.items()))
            return_tree[root_node]=set(list_of_child_node)
            return return_tree

    def get_effective_nodes(self,graph):
        effective_node=[]
        def recursive_on_graph(node):
            effective_node.append(node)
            if node in graph.keys():
                for child_node in graph[node]:
                    recursive_on_graph(child_node)
        recursive_on_graph(0)
        return effective_node
    def count_total_transfer(self,pattern):
        return len(pattern.split('/'))
    def count_token_transfer(self,pattern):
        list_transfer=pattern.split('/')
        total_transfer=len(list_transfer)
        num=0
        for transfer in list_transfer:
            trasnfer_type=transfer.split('_')
            if(trasnfer_type[0]=="transfer" and trasnfer_type[1][0]=="T"):
                num+=1
        return num
    def count_nft_transfer(self,pattern):
        list_transfer=pattern.split('/')
        total_transfer=len(list_transfer)
        num=0
        for transfer in list_transfer:
            trasnfer_type=transfer.split('_')
            if(trasnfer_type[0]=="transfer" and trasnfer_type[1][0]=="N"):
                num+=1
        return num
    def count_vunues(self,pattern):
        list_transfer=pattern.split('/')
        total_transfer=len(list_transfer)
        list_venue=[]
        for transfer in list_transfer:
            trasnfer_type=transfer.split('_')
            list_venue.append(trasnfer_type[2])
            if(len(trasnfer_type)==4):
                list_venue.append(trasnfer_type[3])
        return len(set(list_venue))
    def count_tokens(self,pattern):
        list_transfer=pattern.split('/')
        total_transfer=len(list_transfer)
        list_venue=[]
        for transfer in list_transfer:
            trasnfer_type=transfer.split('_')
            if(trasnfer_type[1][0]=="T"):
                list_venue.append(trasnfer_type[1])
        return len(set(list_venue))
    def count_nfts(self,pattern):
        list_transfer=pattern.split('/')
        total_transfer=len(list_transfer)
        list_venue=[]
        for transfer in list_transfer:
            trasnfer_type=transfer.split('_')
            if(trasnfer_type[1][0]=="N"):
                list_venue.append(trasnfer_type[1])
        return len(set(list_venue))
    def get_pattern_content(self,pattern):
        return_list=[]
        list_transfer=pattern.split('/')
        for transfer in list_transfer:
            transfer_dict={}
            trasnfer_type=transfer.split('_')
            if(trasnfer_type[0]=="transfer"):
                transfer_dict["type"]="transfer"
                transfer_dict["token"]=trasnfer_type[1]
                transfer_dict["from"]=trasnfer_type[2]
                transfer_dict["to"]=trasnfer_type[3]
                if(trasnfer_type[1][0]=="N"):
                    transfer_dict["tokenID"]=True
            elif(trasnfer_type[0]=="mint"):
                transfer_dict["type"]="mint"
                transfer_dict["token"]=trasnfer_type[1]
                transfer_dict["to"]=trasnfer_type[2]
                if(trasnfer_type[1][0]=="N"):
                    transfer_dict["tokenID"]=True
            elif(trasnfer_type[0]=="burn"):
                transfer_dict["type"]="burn"
                transfer_dict["token"]=trasnfer_type[1]
                transfer_dict["from"]=trasnfer_type[2]
                if(trasnfer_type[1][0]=="N"):
                    transfer_dict["tokenID"]=True
            return_list.append(transfer_dict)
        return return_list


    def pattern_match(self,input_pattern, subtree, list_of_parsing, simplify_tree):
        pattern_content = self.get_pattern_content(input_pattern)
        subtree_content = self.get_content(list_of_parsing, simplify_tree, subtree)
        # in pattern_content
        pattern_token_transfer_list = []
        pattern_token_mint_list = []
        pattern_token_burn_list = []
        pattern_nft_transfer_list = []
        pattern_nft_mint_list = []
        pattern_nft_burn_list = []
        for pattern in pattern_content:
            if pattern["type"] == "transfer" and "tokenID" not in pattern.keys():
                pattern_token_transfer_list.append(pattern)
            elif pattern["type"] == "transfer" and "tokenID" in pattern.keys():
                pattern_nft_transfer_list.append(pattern)
            elif pattern["type"] == "mint" and "tokenID" not in pattern.keys():
                pattern_token_mint_list.append(pattern)
            elif pattern["type"] == "burn" and "tokenID" not in pattern.keys():
                pattern_token_burn_list.append(pattern)
            elif pattern["type"] == "mint" and "tokenID" in pattern.keys():
                pattern_nft_mint_list.append(pattern)
            elif pattern["type"] == "burn" and "tokenID" in pattern.keys():
                pattern_nft_burn_list.append(pattern)
                # in subtree_content
        subtree_token_transfer_list = []
        subtree_token_mint_list = []
        subtree_token_burn_list = []
        subtree_nft_transfer_list = []
        subtree_nft_mint_list = []
        subtree_nft_burn_list = []
        for subtree in subtree_content:
            if subtree["type"] == "transfer" and subtree["tokenID"] == "empty":
                subtree_token_transfer_list.append(subtree)
            elif subtree["type"] == "transfer" and subtree["tokenID"] != "empty":
                subtree_nft_transfer_list.append(subtree)
            elif subtree["type"] == "mint" and subtree["tokenID"] == "empty":
                subtree_token_mint_list.append(subtree)
            elif subtree["type"] == "burn" and subtree["tokenID"] == "empty":
                subtree_token_burn_list.append(subtree)
            elif subtree["type"] == "mint" and subtree["tokenID"] != "empty":
                subtree_nft_mint_list.append(subtree)
            elif subtree["type"] == "burn" and subtree["tokenID"] != "empty":
                subtree_nft_burn_list.append(subtree)
        if len(pattern_token_transfer_list) != len(subtree_token_transfer_list):
            return False
        elif len(pattern_token_mint_list) != len(subtree_token_mint_list):
            return False
        elif len(pattern_token_burn_list) != len(subtree_token_burn_list):
            return False
        elif len(pattern_nft_transfer_list) != len(subtree_nft_transfer_list):
            return False
        elif len(pattern_nft_mint_list) != len(subtree_nft_mint_list):
            return False
        elif len(pattern_nft_burn_list) != len(subtree_nft_burn_list):
            return False
        else:
            G1 = nx.MultiDiGraph()
            G2 = nx.MultiDiGraph()
            G1.add_node("Burn", fill="Burn")
            G2.add_node("Burn", fill="Burn")
            G1.add_node("Mint", fill="Mint")
            G2.add_node("Mint", fill="Mint")
            for pattern in pattern_token_transfer_list:
                G1.add_edge(pattern["from"], pattern["to"], token=pattern["token"])
            for pattern in pattern_token_mint_list:
                G1.add_edge("Mint", pattern["to"], token=pattern["token"])
            for pattern in pattern_token_burn_list:
                G1.add_edge(pattern["from"], "Burn", token=pattern["token"])
            for pattern in pattern_nft_transfer_list:
                G1.add_edge(pattern["from"], pattern["to"], nft_token=pattern["token"])
                # nx.add_path(G1,[pattern["from"], pattern["to"]],"nft"=True)
            for pattern in pattern_nft_mint_list:
                G1.add_edge("Mint", pattern["to"], nft_token=pattern["token"])
            for pattern in pattern_nft_burn_list:
                G1.add_edge(pattern["from"], "Burn", nft_token=pattern["token"])

            for pattern in subtree_token_transfer_list:
                G2.add_edge(pattern["from"], pattern["to"], token=pattern["token"])
            for pattern in subtree_token_mint_list:
                G2.add_edge("Mint", pattern["to"], token=pattern["token"])
            for pattern in subtree_token_burn_list:
                G2.add_edge(pattern["from"], "Burn", token=pattern["token"])
            for pattern in subtree_nft_transfer_list:
                G2.add_edge(pattern["from"], pattern["to"], nft_token=str(pattern["tokenID"]))
            for pattern in subtree_nft_mint_list:
                G2.add_edge("Mint", pattern["to"], nft_token=str(pattern["tokenID"]))
            for pattern in subtree_nft_burn_list:
                G2.add_edge(pattern["from"], "Burn", nft_token=str(pattern["tokenID"]))
            nm = iso.categorical_node_match("fill", "Noraml")
            GM = iso.GraphMatcher(G1, G2)
            if GM.is_isomorphic() == False:
                return (False)
            else:
                mapping = GM.mapping
                pattern_token_list = []
                pattern_nft_list = []
                list_transfer = input_pattern.split('/')
                total_transfer = len(list_transfer)
                for transfer in list_transfer:
                    trasnfer_type = transfer.split('_')
                    if (trasnfer_type[1][0] == "T"):
                        pattern_token_list.append(trasnfer_type[1])
                    elif (trasnfer_type[1][0] == "N"):
                        pattern_nft_list.append(trasnfer_type[1])
                pattern_token_set = set(pattern_token_list)
                pattern_nft_set = set(pattern_nft_list)
                pattern_token_dict = {}
                pattern_nft_dict = {}
                for pattern in pattern_token_set:
                    pattern_token_dict[pattern] = []
                for pattern in pattern_nft_set:
                    pattern_nft_dict[pattern] = []
                for edge in G1.edges:
                    if 'token' in G1.edges[edge].keys():
                        if 'token' not in G2[mapping[edge[0]]][mapping[edge[1]]][0].keys():
                            return False
                        else:
                            pattern_token_dict[G1.edges[edge]['token']].append(
                                G2[mapping[edge[0]]][mapping[edge[1]]][0]['token'])
                    elif 'nft_token' in G1.edges[edge].keys():
                        if 'nft_token' not in G2[mapping[edge[0]]][mapping[edge[1]]][0].keys():
                            return False
                        else:
                            pattern_nft_dict[G1.edges[edge]['nft_token']].append(
                                G2[mapping[edge[0]]][mapping[edge[1]]][0]['nft_token'])
                for pattern in pattern_token_dict.keys():
                    pattern_token_dict[pattern] = list(set(pattern_token_dict[pattern]))
                    if (len(pattern_token_dict[pattern]) != 1):
                        return False
                for pattern in pattern_nft_dict.keys():
                    pattern_nft_dict[pattern] = list(set(pattern_nft_dict[pattern]))
                    if (len(pattern_nft_dict[pattern]) != 1):
                        return False
                return True
    def pattern_list_match(self,pattern_list,list_of_parsing,simplify_tree,node):
        for pattern in pattern_list:
            if self.pattern_match(pattern,node,list_of_parsing,simplify_tree):
                return pattern
        else:
            return "not match"
    def pattern_tree_generation(self,pattern_list,list_of_parsing,simplify_tree):
        pattern_structure_list=[]
        def pattern_subtree_generation(pattern_list,list_of_parsing,simplify_treed,node,degree):
            if node not in simplify_tree.keys():
                    return False
            elif self.pattern_list_match(pattern_list,list_of_parsing,simplify_tree,node)!="not match":
                result=self.pattern_list_match(pattern_list,list_of_parsing,simplify_tree,node)
                #viewpoint=list_of_parsing[node]["from"]
                pattern_structure_list.append({"node":result,"degree":degree})
                return True
            else:
                count=0
                for child_node in simplify_tree[node]:
                    child_degree=degree+"-"+str(count)
                    result=pattern_subtree_generation(pattern_list,list_of_parsing,simplify_tree,child_node,child_degree)
                    if result==True:
                        count+=1
                if count>1:
                    #viewpoint=list_of_parsing[node]["from"]
                    pattern_structure_list.append({"node":"empty","degree":degree})
                    return True
                elif count==1:
                    pattern_structure_list.append({"node":"empty","degree":degree})
                    return True
                elif count==0:
                    if self.get_content(list_of_parsing,simplify_tree,node)==[]:
                        return False
                    else:
                        #count+=1
                        #this_degree=degree+"-"+str(count)
                        #viewpoint=list_of_parsing[node]["from"]
                        pattern_structure_list.append({"node":"undiscover_pattern","degree":degree})
                        return True
        pattern_subtree_generation(pattern_list,list_of_parsing,simplify_tree,0,degree="0")
        return pattern_structure_list
    def pattern_parsing(self,frame_list,platformToken,pattern_list):
        list_of_parsing,graph=self.treestructure(frame_list,platformToken)
        simplify_tree=self.generate_new_tree(list_of_parsing,graph,0,{})
        pattern_tree=self.pattern_tree_generation(pattern_list,list_of_parsing,simplify_tree)
        return pattern_tree
    def discriptive_pattern_match(self,input_pattern, subtree, list_of_parsing, simplify_tree):
        pattern_content = self.get_pattern_content(input_pattern)
        subtree_content = self.get_content(list_of_parsing, simplify_tree, subtree)
        # in pattern_content
        pattern_token_transfer_list = []
        pattern_token_mint_list = []
        pattern_token_burn_list = []
        pattern_nft_transfer_list = []
        pattern_nft_mint_list = []
        pattern_nft_burn_list = []
        for pattern in pattern_content:
            if pattern["type"] == "transfer" and "tokenID" not in pattern.keys():
                pattern_token_transfer_list.append(pattern)
            elif pattern["type"] == "transfer" and "tokenID" in pattern.keys():
                pattern_nft_transfer_list.append(pattern)
            elif pattern["type"] == "mint" and "tokenID" not in pattern.keys():
                pattern_token_mint_list.append(pattern)
            elif pattern["type"] == "burn" and "tokenID" not in pattern.keys():
                pattern_token_burn_list.append(pattern)
            elif pattern["type"] == "mint" and "tokenID" in pattern.keys():
                pattern_nft_mint_list.append(pattern)
            elif pattern["type"] == "burn" and "tokenID" in pattern.keys():
                pattern_nft_burn_list.append(pattern)
                # in subtree_content
        subtree_token_transfer_list = []
        subtree_token_mint_list = []
        subtree_token_burn_list = []
        subtree_nft_transfer_list = []
        subtree_nft_mint_list = []
        subtree_nft_burn_list = []
        for subtree in subtree_content:
            if subtree["type"] == "transfer" and subtree["tokenID"] == "empty":
                subtree_token_transfer_list.append(subtree)
            elif subtree["type"] == "transfer" and subtree["tokenID"] != "empty":
                subtree_nft_transfer_list.append(subtree)
            elif subtree["type"] == "mint" and subtree["tokenID"] == "empty":
                subtree_token_mint_list.append(subtree)
            elif subtree["type"] == "burn" and subtree["tokenID"] == "empty":
                subtree_token_burn_list.append(subtree)
            elif subtree["type"] == "mint" and subtree["tokenID"] != "empty":
                subtree_nft_mint_list.append(subtree)
            elif subtree["type"] == "burn" and subtree["tokenID"] != "empty":
                subtree_nft_burn_list.append(subtree)
        if len(pattern_token_transfer_list) != len(subtree_token_transfer_list):
            return False
        elif len(pattern_token_mint_list) != len(subtree_token_mint_list):
            return False
        elif len(pattern_token_burn_list) != len(subtree_token_burn_list):
            return False
        elif len(pattern_nft_transfer_list) != len(subtree_nft_transfer_list):
            return False
        elif len(pattern_nft_mint_list) != len(subtree_nft_mint_list):
            return False
        elif len(pattern_nft_burn_list) != len(subtree_nft_burn_list):
            return False
        else:
            G1 = nx.MultiDiGraph()
            G2 = nx.MultiDiGraph()
            G1.add_node("Burn", fill="Burn")
            G2.add_node("Burn", fill="Burn")
            G1.add_node("Mint", fill="Mint")
            G2.add_node("Mint", fill="Mint")
            for pattern in pattern_token_transfer_list:
                G1.add_edge(pattern["from"], pattern["to"], token=pattern["token"])
            for pattern in pattern_token_mint_list:
                G1.add_edge("Mint", pattern["to"], token=pattern["token"])
            for pattern in pattern_token_burn_list:
                G1.add_edge(pattern["from"], "Burn", token=pattern["token"])
            for pattern in pattern_nft_transfer_list:
                G1.add_edge(pattern["from"], pattern["to"], nft_token=pattern["token"])
                # nx.add_path(G1,[pattern["from"], pattern["to"]],"nft"=True)
            for pattern in pattern_nft_mint_list:
                G1.add_edge("Mint", pattern["to"], nft_token=pattern["token"])
            for pattern in pattern_nft_burn_list:
                G1.add_edge(pattern["from"], "Burn", nft_token=pattern["token"])

            for pattern in subtree_token_transfer_list:
                G2.add_edge(pattern["from"], pattern["to"], token=pattern["token"])
            for pattern in subtree_token_mint_list:
                G2.add_edge("Mint", pattern["to"], token=pattern["token"])
            for pattern in subtree_token_burn_list:
                G2.add_edge(pattern["from"], "Burn", token=pattern["token"])
            for pattern in subtree_nft_transfer_list:
                G2.add_edge(pattern["from"], pattern["to"], nft_token=str(pattern["tokenID"]))
            for pattern in subtree_nft_mint_list:
                G2.add_edge("Mint", pattern["to"], nft_token=str(pattern["tokenID"]))
            for pattern in subtree_nft_burn_list:
                G2.add_edge(pattern["from"], "Burn", nft_token=str(pattern["tokenID"]))
            nm = iso.categorical_node_match("fill", "Noraml")
            GM = iso.GraphMatcher(G1, G2)
            if GM.is_isomorphic() == False:
                return False
            else:
                mapping = GM.mapping
                pattern_token_list = []
                pattern_nft_list = []
                list_transfer = input_pattern.split('/')
                total_transfer = len(list_transfer)
                for transfer in list_transfer:
                    trasnfer_type = transfer.split('_')
                    if (trasnfer_type[1][0] == "T"):
                        pattern_token_list.append(trasnfer_type[1])
                    elif (trasnfer_type[1][0] == "N"):
                        pattern_nft_list.append(trasnfer_type[1])
                pattern_token_set = set(pattern_token_list)
                pattern_nft_set = set(pattern_nft_list)
                pattern_token_dict = {}
                pattern_nft_dict = {}
                for pattern in pattern_token_set:
                    pattern_token_dict[pattern] = []
                for pattern in pattern_nft_set:
                    pattern_nft_dict[pattern] = []
                for edge in G1.edges:
                    if 'token' in G1.edges[edge].keys():
                        if 'token' not in G2[mapping[edge[0]]][mapping[edge[1]]][0].keys():
                            return False
                        else:
                            pattern_token_dict[G1.edges[edge]['token']].append(
                                G2[mapping[edge[0]]][mapping[edge[1]]][0]['token'])
                    elif 'nft_token' in G1.edges[edge].keys():
                        if 'nft_token' not in G2[mapping[edge[0]]][mapping[edge[1]]][0].keys():
                            return False
                        else:
                            pattern_nft_dict[G1.edges[edge]['nft_token']].append(
                                G2[mapping[edge[0]]][mapping[edge[1]]][0]['nft_token'])
                for pattern in pattern_token_dict.keys():
                    pattern_token_dict[pattern] = list(set(pattern_token_dict[pattern]))
                    if (len(pattern_token_dict[pattern]) != 1):
                        return False
                for pattern in pattern_nft_dict.keys():
                    pattern_nft_dict[pattern] = list(set(pattern_nft_dict[pattern]))
                    if (len(pattern_nft_dict[pattern]) != 1):
                        return False
                return [True,mapping,pattern_token_dict,pattern_nft_dict]

    def discriptive_pattern_list_match(self, pattern_list, list_of_parsing, simplify_tree, node):
        for pattern in pattern_list:
            mapping = {}
            pattern_token_dict = {}
            pattern_nft_dict={}
            if self.discriptive_pattern_match(pattern, node, list_of_parsing, simplify_tree)!=False:
                mapping=self.discriptive_pattern_match(pattern, node, list_of_parsing, simplify_tree)[1]
                pattern_token_dict=self.discriptive_pattern_match(pattern, node, list_of_parsing, simplify_tree)[2]
                pattern_nft_dict=self.discriptive_pattern_match(pattern, node, list_of_parsing, simplify_tree)[3]
                return [pattern,mapping,pattern_token_dict,pattern_nft_dict]
        else:
            return "not match"

    def discriptive_pattern_tree_generation(self, pattern_list, list_of_parsing, simplify_tree):
        pattern_structure_list = []
        def discriptive_pattern_subtree_generation(pattern_list, list_of_parsing, simplify_treed, node, degree):
            if node not in simplify_tree.keys():
                return False
            elif self.discriptive_pattern_list_match(pattern_list, list_of_parsing, simplify_tree, node) != "not match":
                result = self.discriptive_pattern_list_match(pattern_list, list_of_parsing, simplify_tree, node)
                # viewpoint=list_of_parsing[node]["from"]
                pattern_structure_list.append({"node": result[0], "degree": degree, "address_mapping":result[1], "token_mapping":result[2], "nft_mapping":result[3]})
                return True
            else:
                count = 0
                for child_node in simplify_tree[node]:
                    child_degree = degree + "-" + str(count)
                    result = discriptive_pattern_subtree_generation(pattern_list, list_of_parsing, simplify_tree, child_node,
                                                        child_degree)
                    if result == True:
                        count += 1
                if count > 1:
                    # viewpoint=list_of_parsing[node]["from"]
                    pattern_structure_list.append({"node": "empty", "degree": degree})
                    return True
                elif count == 1:
                    pattern_structure_list.append({"node": "empty", "degree": degree})
                    return True
                elif count == 0:
                    if self.get_content(list_of_parsing, simplify_tree, node) == []:
                        return False
                    else:
                        # count+=1
                        # this_degree=degree+"-"+str(count)
                        # viewpoint=list_of_parsing[node]["from"]
                        pattern_structure_list.append({"node": "undiscover_pattern", "degree": degree})
                        return True

        discriptive_pattern_subtree_generation(pattern_list, list_of_parsing, simplify_tree, 0, degree="0")
        return pattern_structure_list


