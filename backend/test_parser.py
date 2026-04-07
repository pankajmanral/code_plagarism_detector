import sys
import os
sys.path.append(os.getcwd())

try:
    from ast_parser import ASTParser
    from feature_extractor import FeatureExtractor
    
    code = "def hello(): print('world')"
    parser = ASTParser(language='python')
    tree = parser.parse(code)
    print("Python Parse Success")
    
    extractor = FeatureExtractor(language='python')
    vec = extractor.extract(code)
    print(f"Feature Vector Shape: {vec.shape}")
    
    js_code = "function hello() { console.log('world'); }"
    js_parser = ASTParser(language='javascript')
    js_tree = js_parser.parse(js_code)
    print("JS Parse Success")
    
    js_extractor = FeatureExtractor(language='javascript')
    js_vec = js_extractor.extract(js_code)
    print(f"JS Feature Vector Shape: {js_vec.shape}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
